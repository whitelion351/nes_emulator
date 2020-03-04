class Mapper:
    def __init__(self, prg_banks, chr_banks):
        self.prg_banks = prg_banks
        self.chr_banks = chr_banks

    def cpu_map_read(self, addr, mapped_addr):
        pass

    def cpu_map_write(self, addr, mapped_addr):
        pass

    def ppu_map_read(self, addr, mapped_addr):
        pass

    def ppu_map_write(self, addr, mapped_addr):
        pass


class Mapper000(Mapper):
    def cpu_map_read(self, addr, mapped_addr):
        if 0x8000 <= addr <= 0xFFFF:
            map_mask = 0x7FFF if self.prg_banks > 1 else 0x3FFF
            mapped_addr[0] = addr & map_mask
            return True
        return False

    def cpu_map_write(self, addr, mapped_addr):
        if 0x8000 <= addr <= 0xFFFF:
            map_mask = 0x7FFF if self.prg_banks > 1 else 0x3FFF
            mapped_addr[0] = addr & map_mask
            return True
        return False

    def ppu_map_read(self, addr, mapped_addr):
        if 0x0000 <= addr <= 0x1FFF:
            mapped_addr[0] = addr
            return True
        return False

    def ppu_map_write(self, addr, mapped_addr):
        # if 0x0000 <= addr <= 0x1FFF:
        #     return True
        return False

