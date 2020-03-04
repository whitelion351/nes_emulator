from Cartridge import Cartridge
from OLC6502 import OLC6502
from CPURam import CPURam
from OLC2C02 import OLC2C02


class Bus:
    # Main component of NES Hardware
    def __init__(self):
        self.cpu = OLC6502()
        self.connect_to_bus("cpu", self.cpu)
        self.cpuram = CPURam()
        self.connect_to_bus("cpuram", self.cpuram)
        self.ppu = OLC2C02()
        self.connect_to_bus("ppu", self.ppu)
        self.cart = None
        self.system_clock_counter = 0
        self.please_break = False

    def connect_to_bus(self, dev_type, dev):
        if dev_type == "cpu":
            self.cpu = dev
            self.cpu.bus = self
        elif dev_type == "cpuram":
            self.cpuram = dev
            self.cpuram.bus = self
        elif dev_type == "ppu":
            self.ppu = dev
            self.ppu.bus = self
            self.cpu.ppu = dev
        elif dev_type == "cart":
            self.cart = dev
            self.cart.bus = self
            self.cpu.cart = dev
            self.ppu.cart = dev
        print(dev_type, "is connected")

    def cpu_write(self, addr, data):
        if self.cart.cpu_write(addr, data):
            return
        elif 0x0000 <= addr <= 0x1FFF:
            self.cpuram.ram[addr & 0x07FF] = data
            return
        elif 0x2000 <= addr <= 0x3FFF:
            self.ppu.cpu_write(addr & 0x0007, data)
            return
        else:
            print("No device found at", hex(addr), "cannot write")
            self.please_break = True

    def cpu_read(self, addr, _b_read_only=False):
        data = [0x00]
        if self.cart.cpu_read(addr, data):
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            data[0] = self.cpuram.ram[addr & 0x07FF]
        elif 0x2000 <= addr <= 0x3FFF:
            data[0] = self.ppu.cpu_read(addr & 0x0007)
        else:
            self.please_break = True
            print("No device found at", hex(addr), "cannot read. returning 0x0000")
        return data[0]

    def insert_cart(self, path_to_file=None):
        if not path_to_file:
            print("No path given for cartridge")
            return
        cart_obj = Cartridge(path_to_file)
        self.connect_to_bus("cart", cart_obj)

    def reset(self):
        self.cpu.reset()
        self.system_clock_counter = 0

    def clock(self):
        self.ppu.clock()
        if self.system_clock_counter % 3 == 0:
            self.cpu.clock()
        self.system_clock_counter += 1
