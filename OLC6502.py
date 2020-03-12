from enum import Enum
import numpy as np


class OLC6502:
    # 6502 CPU
    def __init__(self):
        self.bus = None  # Connection to bus
        self.ppu = None  # Connection to ppu
        self.cart = None  # Connection to cartridge
        self.FLAGS6502 = self.FLAGS6502Enums  # Flags Enum
        self.a = np.uint8(0x00)  # Accumulator Register
        self.x = np.uint8(0x00)  # X Register
        self.y = np.uint8(0x00)  # Y Register
        self.stkp = 0xFD  # Stack Pointer (points to location on bus)
        self.pc = 0x00  # Program Counter
        self.status = 0x00  # Status Register
        self.fetched = 0x00
        self.addr_abs = 0x0000
        self.addr_rel = 0x00
        self.opcode = 0x00
        self.opcode_item = None
        self.cycles = 0

        self.debug = False

    class FLAGS6502Enums(Enum):
        # Enumerations for the status register
        C = (1 << 0)  # Carry bit
        Z = (1 << 1)  # Zero
        I = (1 << 2)  # Disable Interrupts
        D = (1 << 3)  # Decimal Mode (unused in this implementation)
        B = (1 << 4)  # Break
        U = (1 << 5)  # Unused
        V = (1 << 6)  # Overflow
        N = (1 << 7)  # Negative

    def write(self, a, d):
        self.bus.cpu_write(a, d)

    def read(self, a):
        return self.bus.cpu_read(a)

    def get_flag(self, f):
        if self.status & f.value > 0:
            return 1
        else:
            return 0

    def set_flag(self, f, v):
        if v:
            self.status |= f.value
        else:
            self.status &= ~f.value

    #######################################################
    # Addressing Modes

    def ACC(self):
        return 0

    def IMP(self):
        self.fetched = self.a
        return 0

    def IMM(self):
        self.addr_abs = self.pc
        self.pc = (self.pc + 1) & 0xFFFF
        return 0

    def ZP0(self):
        self.addr_abs = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        self.addr_abs &= 0x00FF
        return 0

    def ZPX(self):
        self.addr_abs = self.read(self.pc) + self.x
        self.pc = (self.pc + 1) & 0xFFFF
        self.addr_abs &= 0x00FF
        return 0

    def ZPY(self):
        self.addr_abs = self.read(self.pc) + self.y
        self.pc = (self.pc + 1) & 0xFFFF
        self.addr_abs &= 0x00FF
        return 0

    def REL(self):
        self.addr_rel = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        if self.addr_rel & 0x80:
            self.addr_rel = -(self.addr_rel & 0x80) | (self.addr_rel & 0x7f)
        return 0

    def ABS(self):
        lo = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        hi = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        self.addr_abs = (hi << 8) | lo
        return 0

    def ABX(self):
        lo = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        hi = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF

        self.addr_abs = (hi << 8) | lo
        self.addr_abs = (self.addr_abs + self.x) & 0xFFFF
        if (self.addr_abs & 0xFF00) != (hi << 8):
            return 1
        else:
            return 0

    def ABY(self):
        lo = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        hi = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        self.addr_abs = (hi << 8) | lo
        self.addr_abs = (self.addr_abs + self.y) & 0xFFFF
        if (self.addr_abs & 0xFF00) != (hi << 8):
            return 1
        else:
            return 0

    def IND(self):
        ptr_lo = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        ptr_hi = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        ptr = (ptr_hi << 8) | ptr_lo
        if ptr_lo == 0x00FF:
            self.addr_abs = (self.read(ptr & 0xFF00) << 8) | self.read(ptr + 0)
        else:
            self.addr_abs = (self.read(ptr + 1) << 8) | self.read(ptr + 0)
        return 0

    def IZX(self):
        t = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        lo = self.read((t + self.x) & 0x00FF)
        hi = self.read((t + self.x + 1) & 0x00FF)
        self.addr_abs = (hi << 8) | lo
        return 0

    def IZY(self):
        t = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        lo = self.read(t & 0x00FF)
        hi = self.read((t + 1) & 0x00FF)
        self.addr_abs = (hi << 8) | lo
        self.addr_abs = (self.addr_abs + self.y) & 0xFFFF
        if (self.addr_abs & 0xFF00) != (hi << 8):
            return 1
        else:
            return 0

    #######################################################
    # Operations
    def ADC(self):
        self.fetch()
        temp = self.a + self.fetched + self.get_flag(self.FLAGS6502.C)
        self.set_flag(self.FLAGS6502.C, temp > 255)
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0)
        self.set_flag(self.FLAGS6502.V, (~(self.a ^ self.fetched) & (self.a ^ temp)) & 0x0080)
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        self.a = temp & 0x00FF
        return 1

    def AND(self):
        self.fetch()
        self.a = self.a & self.fetched
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        return 1

    def ASL(self):
        self.fetch()
        self.set_flag(self.FLAGS6502.C, (self.fetched & 0x80))
        temp = (self.fetched << 1) & 0xFF
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        self.set_flag(self.FLAGS6502.Z, (temp & 0xFF) == 0x00)
        if self.opcode_item.addr_mode.__name__ == "IMP":
            self.a = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)
        return 0

    def BCC(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.C) == 0:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BCS(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.C) == 1:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BEQ(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.Z) == 1:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BIT(self):
        self.fetch()
        temp = self.a & self.fetched
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0x00)
        self.set_flag(self.FLAGS6502.N, self.fetched & (1 << 7))
        self.set_flag(self.FLAGS6502.V, self.fetched & (1 << 6))
        return 0

    def BMI(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.N) == 1:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BNE(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.Z) == 0:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BPL(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.N) == 0:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BRK(self):
        self.pc = (self.pc + 1) & 0xFFFF
        self.write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
        self.stkp = (self.stkp - 1) % 256
        self.write(0x0100 + self.stkp, self.pc & 0x00FF)
        self.stkp = (self.stkp - 1) % 256

        self.set_flag(self.FLAGS6502.B, 1)
        self.write(0x0100 + self.stkp, self.status)
        self.stkp = (self.stkp - 1) % 256
        self.set_flag(self.FLAGS6502.I, 1)

        self.pc = self.read(0xFFFE) | (self.read(0xFFFF) << 8)
        return 0

    def BVC(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.V) == 0:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def BVS(self):
        self.addr_abs = (self.pc + self.addr_rel) & 0xFFFF
        if self.get_flag(self.FLAGS6502.V) == 1:
            self.cycles += 1
            if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1
            self.pc = self.addr_abs
        return 0

    def CLC(self):
        self.set_flag(self.FLAGS6502.C, False)
        return 0

    def CLD(self):
        self.set_flag(self.FLAGS6502.D, False)
        return 0

    def CLI(self):
        self.set_flag(self.FLAGS6502.I, False)
        return 0

    def CLV(self):
        self.set_flag(self.FLAGS6502.V, False)
        return 0

    def CMP(self):
        self.fetch()
        temp = (self.a - self.fetched) & 0xFF
        self.set_flag(self.FLAGS6502.C, self.a >= self.fetched)
        self.set_flag(self.FLAGS6502.Z, temp == 0x00)
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        return 1

    def CPX(self):
        self.fetch()
        temp = (self.x - self.fetched) & 0xFF
        self.set_flag(self.FLAGS6502.C, self.x >= self.fetched)
        self.set_flag(self.FLAGS6502.Z, temp == 0x00)
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        return 0

    def CPY(self):
        self.fetch()
        temp = (self.y - self.fetched) & 0xFF
        self.set_flag(self.FLAGS6502.C, self.y >= self.fetched)
        self.set_flag(self.FLAGS6502.Z, temp == 0x00)
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        return 0

    def DEC(self):
        self.fetch()
        temp = (self.fetched - 1) % 256
        self.write(self.addr_abs, temp & 0x00FF)
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(self.FLAGS6502.N, temp & 0x0080)
        return 0

    def DEX(self):
        self.x = (self.x - 1) % 256
        self.set_flag(self.FLAGS6502.Z, self.x == 0x00)
        self.set_flag(self.FLAGS6502.N, self.x & 0x80)
        return 0

    def DEY(self):
        self.y = (self.y - 1) % 256
        self.set_flag(self.FLAGS6502.Z, self.y == 0x00)
        self.set_flag(self.FLAGS6502.N, self.y & 0x80)
        return 0

    def EOR(self):
        self.fetch()
        self.a = self.a ^ self.fetched
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 1

    def INC(self):
        self.fetch()
        temp = (self.fetched + 1) % 256
        self.write(self.addr_abs, (temp & 0x00FF))
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(self.FLAGS6502.N, temp & 0x0080)
        return 0

    def INX(self):
        self.x = (self.x + 1) % 256
        self.set_flag(self.FLAGS6502.Z, self.x == 0x00)
        self.set_flag(self.FLAGS6502.N, self.x & 0x80)
        return 0

    def INY(self):
        self.y = (self.y + 1) % 256
        self.set_flag(self.FLAGS6502.Z, self.y == 0x00)
        self.set_flag(self.FLAGS6502.N, self.y & 0x80)
        return 0

    def JMP(self):
        self.pc = self.addr_abs
        return 0

    def JSR(self):
        self.pc -= 1
        self.write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
        self.stkp = (self.stkp - 1) % 256
        self.write(0x0100 + self.stkp, self.pc & 0x00FF)
        self.stkp = (self.stkp - 1) % 256
        self.pc = self.addr_abs
        return 0

    def LDA(self):
        self.fetch()
        self.a = self.fetched
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 1

    def LDX(self):
        self.fetch()
        self.x = self.fetched
        self.set_flag(self.FLAGS6502.Z, self.x == 0x00)
        self.set_flag(self.FLAGS6502.N, self.x & 0x80)
        return 1

    def LDY(self):
        self.fetch()
        self.y = self.fetched
        self.set_flag(self.FLAGS6502.Z, self.y == 0x00)
        self.set_flag(self.FLAGS6502.N, self.y & 0x80)
        return 1

    def LSR(self):
        self.fetch()
        self.set_flag(self.FLAGS6502.C, self.fetched & 0x0001)
        temp = self.fetched >> 1
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(self.FLAGS6502.N, temp & 0x0080)
        if self.opcode_item.addr_mode.__name__ == "IMP":
            self.a = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)
        return 0

    def NOP(self):
        if self.opcode == 0xFC:
            return 1
        else:
            return 0

    def ORA(self):
        self.fetch()
        self.a = self.a | self.fetched
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 1

    def PHA(self):
        self.write(0x0100 + self.stkp, self.a)
        self.stkp = (self.stkp - 1) % 256
        return 0

    def PHP(self):
        self.write(0x0100 + self.stkp, self.status | self.FLAGS6502.B.value | self.FLAGS6502.U.value)
        self.stkp = (self.stkp - 1) % 256
        return 0

    def PLA(self):
        self.stkp = (self.stkp + 1) % 256
        self.a = self.read(0x0100 + self.stkp)
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 0

    def PLP(self):
        self.stkp = (self.stkp + 1) % 256
        self.status = self.read(0x0100 + self.stkp)
        self.set_flag(self.FLAGS6502.U, 1)
        return 0

    def ROL(self):
        self.fetch()
        temp = (self.fetched << 1)
        if self.get_flag(self.FLAGS6502.C):
            temp |= 0x1
        self.set_flag(self.FLAGS6502.C, temp > 0xFF)
        temp &= 0xFF
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        self.set_flag(self.FLAGS6502.Z, temp == 0x0)
        if self.opcode_item.addr_mode.__name__ == "IMP":
            self.a = temp
        else:
            self.write(self.addr_abs, temp)
        return 0

    def ROR(self):
        self.fetch()
        temp = self.fetched
        if self.get_flag(self.FLAGS6502.C):
            temp |= 0x100
        self.set_flag(self.FLAGS6502.C, temp & 0x01)
        temp = temp >> 1
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        self.set_flag(self.FLAGS6502.Z, temp == 0x0)
        if self.opcode_item.addr_mode.__name__ == "IMP":
            self.a = temp & 0xFF
        else:
            self.write(self.addr_abs, temp & 0xFF)
        return 0

    def RTI(self):
        self.stkp = (self.stkp + 1) % 256
        self.status = self.read(0x0100 + self.stkp)
        self.stkp = (self.stkp + 1) % 256
        self.pc = self.read(0x0100 + self.stkp)
        self.stkp = (self.stkp + 1) % 256
        self.pc |= (self.read(0x0100 + self.stkp) << 8)
        return 0

    def RTS(self):
        self.stkp = (self.stkp + 1) % 256
        self.pc = self.read(0x0100 + self.stkp)
        self.stkp = (self.stkp + 1) % 256
        self.pc |= (self.read(0x0100 + self.stkp) << 8)
        self.pc = (self.pc + 1) & 0xFFFF
        return 0

    def SBC(self):
        self.fetch()
        value = self.fetched ^ 0x00FF
        temp = np.uint16(self.a + value + self.get_flag(self.FLAGS6502.C))
        self.set_flag(self.FLAGS6502.C, temp & 0xFF00)
        self.set_flag(self.FLAGS6502.Z, (temp & 0x00FF) == 0x00)
        self.set_flag(self.FLAGS6502.V, (temp ^ self.a) & (temp ^ value) & 0x80)
        self.set_flag(self.FLAGS6502.N, temp & 0x80)
        self.a = (temp & 0xFF)
        return 1

    def SEC(self):
        self.set_flag(self.FLAGS6502.C, True)
        return 0

    def SED(self):
        self.set_flag(self.FLAGS6502.D, True)
        return 0

    def SEI(self):
        self.set_flag(self.FLAGS6502.I, True)
        return 0

    def STA(self):
        self.write(self.addr_abs, self.a)
        return 0

    def STX(self):
        self.write(self.addr_abs, self.x)
        return 0

    def STY(self):
        self.write(self.addr_abs, self.y)
        return 0

    def TAX(self):
        self.x = self.a % 256
        self.set_flag(self.FLAGS6502.Z, self.x == 0x00)
        self.set_flag(self.FLAGS6502.N, self.x & 0x80)
        return 0

    def TAY(self):
        self.y = self.a % 256
        self.set_flag(self.FLAGS6502.Z, self.y == 0x00)
        self.set_flag(self.FLAGS6502.N, self.y & 0x80)
        return 0

    def TSX(self):
        self.x = self.stkp % 256
        self.set_flag(self.FLAGS6502.Z, self.x == 0x00)
        self.set_flag(self.FLAGS6502.N, self.x & 0x80)
        return 0

    def TXA(self):
        self.a = self.x % 256
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 0

    def TXS(self):
        self.stkp = self.x % 256
        return 0

    def TYA(self):
        self.a = self.y % 256
        self.set_flag(self.FLAGS6502.Z, self.a == 0x00)
        self.set_flag(self.FLAGS6502.N, self.a & 0x80)
        return 0

    def XXX(self):
        return 0

    #######################################################
    # Unofficial Opcodes

    def LAX(self):
        self.LDA()
        self.TAX()
        return 1

    #######################################################
    # External Signals

    def clock(self):
        if self.cycles == 0:
            self.opcode = self.read(self.pc)
            self.opcode_item = self.do_lookup(self.opcode)
            # if self.opcode_item.name == "???":
            #     print("addr {} ran illegal opcode {} {}".format(hex(self.pc), hex(self.opcode), self.opcode_item.name))
            #     self.debug = True
            # if self.debug is True or hex(self.pc) == "0xe4da":  # or self.opcode_item.addr_mode.__name__ == "ABX" or hex(self.pc) == "0xe1e2":
            #     print("addr: {} op: {} {} {}".format(hex(self.pc), hex(self.opcode), self.opcode_item.addr_mode.__name__, self.opcode_item.name), end=" ")
            #     self.debug = True
            self.set_flag(self.FLAGS6502.U, True)
            self.pc = (self.pc + 1) & 0xFFFF
            self.cycles = self.opcode_item.cycles
            additional_cycle1 = self.opcode_item.addr_mode(self)
            additional_cycle2 = self.opcode_item.operation(self)
            self.cycles += (additional_cycle1 + additional_cycle2)
            # if self.debug is True:
            #     print("f: {} abs: {} rel: {} l_d: {}".format(hex(self.fetched), hex(self.addr_abs), hex(self.addr_rel), hex(self.read(self.addr_abs))))
            # status_string = ""
            # status_string += "C " if self.get_flag(self.FLAGS6502.C) else "c "
            # status_string += "Z " if self.get_flag(self.FLAGS6502.Z) else "z "
            # status_string += "I " if self.get_flag(self.FLAGS6502.I) else "i "
            # status_string += "D " if self.get_flag(self.FLAGS6502.D) else "d "
            # status_string += "B " if self.get_flag(self.FLAGS6502.B) else "b "
            # status_string += "U " if self.get_flag(self.FLAGS6502.U) else "u "
            # status_string += "V " if self.get_flag(self.FLAGS6502.V) else "v "
            # status_string += "N" if self.get_flag(self.FLAGS6502.N) else "n"
            # if self.debug is True:
            #     print("ram:", self.bus.cpuram.ram[0x0:0x11], "A: {} X: {} Y: {}".format(hex(self.a), hex(self.x), hex(self.y)), status_string)
            #     a = input("1 to skip, any other to step: ")
            #     if a == "1":
            #         self.debug = False

            self.set_flag(self.FLAGS6502.U, True)

        self.cycles -= 1

    def reset(self):
        self.addr_abs = 0xFFFC
        lo = self.read(self.addr_abs + 0)
        hi = self.read(self.addr_abs + 1)
        self.pc = (hi << 8) | lo
        print("starting at", hex(self.pc))
        self.a = 0
        self.x = 0
        self.y = 0
        self.stkp = 0xFD
        self.status = 0x00 | self.FLAGS6502.U.value
        self.addr_abs = 0x0000
        self.addr_rel = 0x0000
        self.fetched = 0x00
        self.cycles = 8

    def irq(self):
        # If interrupts are allowed
        if self.get_flag(self.FLAGS6502.I) == 0:
            # Push the program counter to the stack. It's 16-bits don't forget so that takes two pushes
            self.write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
            self.stkp = (self.stkp - 1) % 256
            self.write(0x0100 + self.stkp, self.pc & 0x00FF)
            self.stkp = (self.stkp - 1) % 256
            # Then Push the status register to the stack
            self.write(0x0100 + self.stkp, self.status)
            self.stkp = (self.stkp - 1) % 256
            self.set_flag(self.FLAGS6502.B, 0)
            self.set_flag(self.FLAGS6502.U, 1)
            self.set_flag(self.FLAGS6502.I, 1)
            # Read new program counter location from fixed address
            self.addr_abs = 0xFFFE
            lo = self.read(self.addr_abs + 0)
            hi = self.read(self.addr_abs + 1)
            self.pc = (hi << 8) | lo
            # IRQs take time
            self.cycles = 7

    def nmi(self):
        # A Non - Maskable Interrupt cannot be ignored. It behaves in exactly the same way as a regular IRQ,
        # but reads the new program counter address from location 0xFFFA.

        # Push the program counter to the stack. It's 16-bits don't forget so that takes two pushes
        self.write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
        self.stkp = (self.stkp - 1) % 256
        self.write(0x0100 + self.stkp, self.pc & 0x00FF)
        self.stkp = (self.stkp - 1) % 256
        # Then Push the status register to the stack
        self.set_flag(self.FLAGS6502.B, 0)
        self.set_flag(self.FLAGS6502.U, 1)
        self.set_flag(self.FLAGS6502.I, 1)
        self.write(0x0100 + self.stkp, self.status)
        self.stkp = (self.stkp - 1) % 256
        # Read new program counter location from fixed address
        self.addr_abs = 0xFFFA
        lo = self.read(self.addr_abs + 0)
        hi = self.read(self.addr_abs + 1)
        self.pc = (hi << 8) | lo
        # IRQs take time
        self.cycles = 7

    #######################################################
    # Lookup Table and helper class for getting correct address mode and operation based on opcode
    class LookupItem:
        def __init__(self, name, operation, addr_mode, cycles):
            self.name = name
            self.addr_mode = addr_mode
            self.operation = operation
            self.cycles = cycles

    lookup = [
        [LookupItem("BRK", BRK, IMM, 7), LookupItem("ORA", ORA, IZX, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 3), LookupItem("ORA", ORA, ZP0, 3), LookupItem("ASL", ASL, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("PHP", PHP, IMP, 3), LookupItem("ORA", ORA, IMM, 2), LookupItem("ASL", ASL, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("NOP", NOP, IMP, 4), LookupItem("ORA", ORA, ABS, 4), LookupItem("ASL", ASL, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BPL", BPL, REL, 2), LookupItem("ORA", ORA, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("ORA", ORA, ZPX, 4), LookupItem("ASL", ASL, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("CLC", CLC, IMP, 2), LookupItem("ORA", ORA, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("ORA", ORA, ABX, 4), LookupItem("ASL", ASL, ABX, 7), LookupItem("???", XXX, IMP, 7)],
        [LookupItem("JSR", JSR, ABS, 6), LookupItem("AND", AND, IZX, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("BIT", BIT, ZP0, 3), LookupItem("AND", AND, ZP0, 3), LookupItem("ROL", ROL, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("PLP", PLP, IMP, 4), LookupItem("AND", AND, IMM, 2), LookupItem("ROL", ROL, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("BIT", BIT, ABS, 4), LookupItem("AND", AND, ABS, 4), LookupItem("ROL", ROL, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BMI", BMI, REL, 2), LookupItem("AND", AND, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("AND", AND, ZPX, 4), LookupItem("ROL", ROL, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("SEC", SEC, IMP, 2), LookupItem("AND", AND, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("AND", AND, ABX, 4), LookupItem("ROL", ROL, ABX, 7), LookupItem("???", XXX, IMP, 7)],
        [LookupItem("RTI", RTI, IMP, 6), LookupItem("EOR", EOR, IZX, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 3), LookupItem("EOR", EOR, ZP0, 3), LookupItem("LSR", LSR, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("PHA", PHA, IMP, 3), LookupItem("EOR", EOR, IMM, 2), LookupItem("LSR", LSR, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("JMP", JMP, ABS, 3), LookupItem("EOR", EOR, ABS, 4), LookupItem("LSR", LSR, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BVC", BVC, REL, 2), LookupItem("EOR", EOR, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("EOR", EOR, ZPX, 4), LookupItem("LSR", LSR, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("CLI", CLI, IMP, 2), LookupItem("EOR", EOR, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("EOR", EOR, ABX, 4), LookupItem("LSR", LSR, ABX, 7), LookupItem("???", XXX, IMP, 7)],
        [LookupItem("RTS", RTS, IMP, 6), LookupItem("ADC", ADC, IZX, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 3), LookupItem("ADC", ADC, ZP0, 3), LookupItem("ROR", ROR, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("PLA", PLA, IMP, 4), LookupItem("ADC", ADC, IMM, 2), LookupItem("ROR", ROR, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("JMP", JMP, IND, 5), LookupItem("ADC", ADC, ABS, 4), LookupItem("ROR", ROR, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BVS", BVS, REL, 2), LookupItem("ADC", ADC, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("ADC", ADC, ZPX, 4), LookupItem("ROR", ROR, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("SEI", SEI, IMP, 2), LookupItem("ADC", ADC, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("ADC", ADC, ABX, 4), LookupItem("ROR", ROR, ABX, 7), LookupItem("???", XXX, IMP, 7)],
        [LookupItem("NOP", NOP, IMP, 2), LookupItem("STA", STA, IZX, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 6), LookupItem("STY", STY, ZP0, 3), LookupItem("STA", STA, ZP0, 3), LookupItem("STX", STX, ZP0, 3), LookupItem("???", XXX, IMP, 3), LookupItem("DEY", DEY, IMP, 2), LookupItem("NOP", NOP, IMM, 2), LookupItem("TXA", TXA, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("STY", STY, ABS, 4), LookupItem("STA", STA, ABS, 4), LookupItem("STX", STX, ABS, 4), LookupItem("???", XXX, IMP, 4)],
        [LookupItem("BCC", BCC, REL, 2), LookupItem("STA", STA, IZY, 6), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 6), LookupItem("STY", STY, ZPX, 4), LookupItem("STA", STA, ZPX, 4), LookupItem("STX", STX, ZPY, 4), LookupItem("???", XXX, IMP, 4), LookupItem("TYA", TYA, IMP, 2), LookupItem("STA", STA, ABY, 5), LookupItem("TXS", TXS, IMP, 2), LookupItem("???", XXX, IMP, 5), LookupItem("NOP", NOP, IMP, 5), LookupItem("STA", STA, ABX, 5), LookupItem("???", XXX, IMP, 5), LookupItem("???", XXX, IMP, 5)],
        [LookupItem("LDY", LDY, IMM, 2), LookupItem("LDA", LDA, IZX, 6), LookupItem("LDX", LDX, IMM, 2), LookupItem("LAX", LAX, IZX, 6), LookupItem("LDY", LDY, ZP0, 3), LookupItem("LDA", LDA, ZP0, 3), LookupItem("LDX", LDX, ZP0, 3), LookupItem("???", XXX, IMP, 3), LookupItem("TAY", TAY, IMP, 2), LookupItem("LDA", LDA, IMM, 2), LookupItem("TAX", TAX, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("LDY", LDY, ABS, 4), LookupItem("LDA", LDA, ABS, 4), LookupItem("LDX", LDX, ABS, 4), LookupItem("???", XXX, IMP, 4)],
        [LookupItem("BCS", BCS, REL, 2), LookupItem("LDA", LDA, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 5), LookupItem("LDY", LDY, ZPX, 4), LookupItem("LDA", LDA, ZPX, 4), LookupItem("LDX", LDX, ZPY, 4), LookupItem("???", XXX, IMP, 4), LookupItem("CLV", CLV, IMP, 2), LookupItem("LDA", LDA, ABY, 4), LookupItem("TSX", TSX, IMP, 2), LookupItem("???", XXX, IMP, 4), LookupItem("LDY", LDY, ABX, 4), LookupItem("LDA", LDA, ABX, 4), LookupItem("LDX", LDX, ABY, 4), LookupItem("???", XXX, IMP, 4)],
        [LookupItem("CPY", CPY, IMM, 2), LookupItem("CMP", CMP, IZX, 6), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("CPY", CPY, ZP0, 3), LookupItem("CMP", CMP, ZP0, 3), LookupItem("DEC", DEC, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("INY", INY, IMP, 2), LookupItem("CMP", CMP, IMM, 2), LookupItem("DEX", DEX, IMP, 2), LookupItem("???", XXX, IMP, 2), LookupItem("CPY", CPY, ABS, 4), LookupItem("CMP", CMP, ABS, 4), LookupItem("DEC", DEC, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BNE", BNE, REL, 2), LookupItem("CMP", CMP, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("CMP", CMP, ZPX, 4), LookupItem("DEC", DEC, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("CLD", CLD, IMP, 2), LookupItem("CMP", CMP, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("CMP", CMP, ABX, 4), LookupItem("DEC", DEC, ABX, 7), LookupItem("???", XXX, IMP, 7)],
        [LookupItem("CPX", CPX, IMM, 2), LookupItem("SBC", SBC, IZX, 6), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("CPX", CPX, ZP0, 3), LookupItem("SBC", SBC, ZP0, 3), LookupItem("INC", INC, ZP0, 5), LookupItem("???", XXX, IMP, 5), LookupItem("INX", INX, IMP, 2), LookupItem("SBC", SBC, IMM, 2), LookupItem("NOP", NOP, IMP, 2), LookupItem("SBC", SBC, IMP, 2), LookupItem("CPX", CPX, ABS, 4), LookupItem("SBC", SBC, ABS, 4), LookupItem("INC", INC, ABS, 6), LookupItem("???", XXX, IMP, 6)],
        [LookupItem("BEQ", BEQ, REL, 2), LookupItem("SBC", SBC, IZY, 5), LookupItem("???", XXX, IMP, 2), LookupItem("???", XXX, IMP, 8), LookupItem("NOP", NOP, IMP, 4), LookupItem("SBC", SBC, ZPX, 4), LookupItem("INC", INC, ZPX, 6), LookupItem("???", XXX, IMP, 6), LookupItem("SED", SED, IMP, 2), LookupItem("SBC", SBC, ABY, 4), LookupItem("NOP", NOP, IMP, 2), LookupItem("???", XXX, IMP, 7), LookupItem("NOP", NOP, IMP, 4), LookupItem("SBC", SBC, ABX, 4), LookupItem("INC", INC, ABX, 7), LookupItem("???", XXX, IMP, 7)],
    ]

    # Other Helper functions
    def fetch(self):
        if self.opcode_item.addr_mode.__name__ != "IMP":
            self.fetched = self.read(self.addr_abs)
        return self.fetched

    def do_lookup(self, opcode):
        hi = (opcode & 0xF0) >> 4
        lo = opcode & 0x0F
        return self.lookup[hi][lo]