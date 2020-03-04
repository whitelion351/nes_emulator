from Mappers import Mapper000


class Cartridge:
    def __init__(self, file_path):
        self.bus = None
        self.file_path = file_path
        self.cart_header = self.CartHeader()
        self.PRG_memory = []
        self.CHR_memory = []
        self.mapperID = 0
        self.PRG_bank_amount = 0
        self.CHR_bank_amount = 0
        self.mapper = None
        self.load_rom()

    class CartHeader:
        def __init__(self):
            self.name = ""
            self.prg_chunks = 0
            self.chr_chunks = 0
            self.mapper1 = 0
            self.mapper2 = 0
            self.prg_ram_size = 0
            self.tv_system1 = 0
            self.tv_system2 = 0
            self.unused = ""

    def load_rom(self):
        with open(self.file_path, "rb") as rom:
            self.cart_header.name = rom.read(4).decode("utf-8")
            print("name", self.cart_header.name)

            self.cart_header.prg_chunks = int().from_bytes(rom.read(1), byteorder="little")
            print("prg chunks", self.cart_header.prg_chunks)

            self.cart_header.chr_chunks = int().from_bytes(rom.read(1), byteorder="little")
            print("chr chunks", self.cart_header.chr_chunks)

            self.cart_header.mapper1 = int().from_bytes(rom.read(1), byteorder="little")
            print("mapper1", self.cart_header.mapper1)

            self.cart_header.mapper2 = int().from_bytes(rom.read(1), byteorder="little")
            print("mapper2", self.cart_header.mapper2)

            self.cart_header.prg_ram_size = int().from_bytes(rom.read(1), byteorder="little")
            print("prg ram size", self.cart_header.prg_ram_size)

            self.cart_header.tv_system1 = int().from_bytes(rom.read(1), byteorder="little")
            print("tv system1", self.cart_header.tv_system1)

            self.cart_header.tv_system2 = int().from_bytes(rom.read(1), byteorder="little")
            print("tv system2", self.cart_header.tv_system2)

            self.cart_header.unused = rom.read(5)
            print("unused", self.cart_header.unused)

            if self.cart_header.mapper1 & 0x04:
                rom.read(512)

            self.mapperID = ((self.cart_header.mapper2 >> 4) << 4) | (self.cart_header.mapper1 >> 4)
            print("mapperID =", self.mapperID)

            file_type = 1

            if file_type == 0:
                pass
            elif file_type == 1:
                self.PRG_bank_amount = self.cart_header.prg_chunks
                self.PRG_memory = [0 for _ in range(self.PRG_bank_amount * 16384)]
                self.PRG_memory[:] = rom.read(len(self.PRG_memory))

                self.CHR_bank_amount = self.cart_header.chr_chunks
                self.CHR_memory = [0 for _ in range(self.CHR_bank_amount * 8192)]
                self.CHR_memory[:] = rom.read(len(self.CHR_memory))

            elif file_type == 2:
                pass
            if self.mapperID == 0:
                print("selected Mapper000")
                self.mapper = Mapper000(self.PRG_bank_amount, self.CHR_bank_amount)
            else:
                print("Mapper{} not implemented yet".format(self.mapperID))
                return None

    def cpu_read(self, addr, data):
        mapped_addr = [0]
        if self.mapper.cpu_map_read(addr, mapped_addr):
            data[0] = self.PRG_memory[mapped_addr[0]]
            return True
        else:
            return False

    def cpu_write(self, addr, data):
        mapped_addr = [0]
        if self.mapper.cpu_map_write(addr, mapped_addr):
            self.PRG_memory[mapped_addr[0]] = data
            return True
        else:
            return False

    def ppu_read(self, addr, data):
        mapped_addr = [0]
        if self.mapper.ppu_map_read(addr, mapped_addr):
            data[0] = self.CHR_memory[mapped_addr[0]]
            return True
        else:
            return False

    def ppu_write(self, addr, data):
        mapped_addr = [0]
        if self.mapper.ppu_map_write(addr, mapped_addr):
            self.CHR_memory[mapped_addr[0]] = data
            return True
        else:
            return False
