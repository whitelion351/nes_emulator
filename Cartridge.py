from Mappers import Mapper000
from enum import Enum


class MIRROR(Enum):
    # Enumerations for the status register
    HORIZONTAL = 0
    VERTICAL = 1
    ONESCREEN_LO = 2
    ONESCREEN_HI = 3


class Cartridge:
    def __init__(self, file_path):
        self.bus = None
        self.file_path = file_path
        self.header = self.CartHeader()
        self.MIRROR = MIRROR
        self.mirror = MIRROR.HORIZONTAL  # default is HORIZONTAL
        self.mapperID = 0
        self.PRG_banks = 0
        self.CHR_banks = 0
        self.PRG_memory = []
        self.CHR_memory = []
        self.mapper = None
        self.load_rom()

    class CartHeader:
        def __init__(self):
            self.name = ""
            self.prg_rom_chunks = 0
            self.chr_rom_chunks = 0
            self.mapper1 = 0
            self.mapper2 = 0
            self.prg_ram_size = 0
            self.tv_system1 = 0
            self.tv_system2 = 0
            self.unused = ""

    def load_rom(self):
        with open(self.file_path, "rb") as rom:
            self.header.name = rom.read(4).decode("utf-8")
            print("name", self.header.name)

            self.header.prg_rom_chunks = int().from_bytes(rom.read(1), byteorder="little")
            self.header.chr_rom_chunks = int().from_bytes(rom.read(1), byteorder="little")
            print("prg rom chunks", self.header.prg_rom_chunks, "chr rom chunks", self.header.chr_rom_chunks)

            self.header.mapper1 = int().from_bytes(rom.read(1), byteorder="little")
            self.header.mapper2 = int().from_bytes(rom.read(1), byteorder="little")
            print("mapper1", self.header.mapper1, "mapper2", self.header.mapper2)

            self.header.prg_ram_size = int().from_bytes(rom.read(1), byteorder="little")
            print("prg ram size", self.header.prg_ram_size)

            self.header.tv_system1 = int().from_bytes(rom.read(1), byteorder="little")
            self.header.tv_system2 = int().from_bytes(rom.read(1), byteorder="little")
            print("tv system1", self.header.tv_system1, "tv system2", self.header.tv_system2)

            self.header.unused = rom.read(5)

            if self.header.mapper1 & 0x04:
                rom.read(512)

            self.mapperID = ((self.header.mapper2 >> 4) << 4) | (self.header.mapper1 >> 4)
            print("mapperID ", self.mapperID)
            self.mirror = MIRROR.VERTICAL if (self.header.mapper1 & 0x01) else MIRROR.HORIZONTAL

            print("mirror mode", "vertical" if self.mirror == MIRROR.VERTICAL else "horizontal")

            file_type = 1

            if file_type == 0:
                pass
            elif file_type == 1:
                self.PRG_banks = self.header.prg_rom_chunks
                self.PRG_memory = [0 for _ in range(self.PRG_banks * 16384)]
                self.PRG_memory[:] = rom.read(len(self.PRG_memory))

                self.CHR_banks = self.header.chr_rom_chunks
                if self.CHR_banks == 0:
                    self.CHR_memory = [0 for _ in range(8192)]
                else:
                    self.CHR_memory = [0 for _ in range(self.CHR_banks * 8192)]
                self.CHR_memory[:] = rom.read(len(self.CHR_memory))

            elif file_type == 2:
                pass
            if self.mapperID == 0:
                print("selected Mapper000")
                self.mapper = Mapper000(self.PRG_banks, self.CHR_banks)
            else:
                print("Mapper{} not implemented yet".format(self.mapperID))
                return None

    def cpu_read(self, addr, data):
        mapped_addr = [0]
        if self.mapper.cpu_map_read(addr, mapped_addr):
            data[0] = self.PRG_memory[mapped_addr[0]]
            # print("{} -> {} = {} reading from cartridge PRG mem".format(hex(addr), hex(mapped_addr[0]), hex(data[0])))
            return True
        else:
            return False

    def cpu_write(self, addr, data):
        mapped_addr = [0]
        if self.mapper.cpu_map_write(addr, mapped_addr):
            self.PRG_memory[mapped_addr[0]] = data
            # print("{} -> {} = {} writing to cartridge PRG mem".format(hex(addr), hex(mapped_addr[0]), hex(data)))
            return True
        else:
            return False

    def ppu_read(self, addr, data):
        mapped_addr = [0]
        if self.mapper.ppu_map_read(addr, mapped_addr):
            data[0] = self.CHR_memory[mapped_addr[0]]
            # print("{} -> {} = {} reading from cartridge CHR mem".format(hex(addr), hex(mapped_addr[0]), hex(data[0])))
            return True
        else:
            return False

    def ppu_write(self, addr, data):
        mapped_addr = [0]
        if self.mapper.ppu_map_write(addr, mapped_addr):
            self.CHR_memory[mapped_addr[0]] = data
            # print("{} -> {} = {} writing to cartridge CHR mem".format(hex(addr), hex(mapped_addr[0]), hex(data)))
            return True
        else:
            return False
