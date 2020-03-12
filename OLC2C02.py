import cv2
import numpy as np
from Registers import PPUStatusRegister, PPUControlRegister, PPUMaskRegister, LoopyRegister, Shifter16Bit


class OLC2C02:
    def __init__(self):

        self.cycler = 0

        self.bus = None
        self.cart = None
        self.name_table = [[0 for _ in range(1024)] for _ in range(2)]
        self.palette_table = [0 for _ in range(32)]
        self.pattern_table = [[0 for _ in range(4096)] for _ in range(2)]
        self.screen_size_x = 256
        self.screen_size_y = 240
        self.screen_image = [[(0, 0, 0) for _ in range(256)] for _ in range(240)]

        self.selected_palette = 0
        self.screen_palette = [(0, 0, 0) for _ in range(0x40)]
        self.name_table_sprite = np.zeros((2, 240, 256, 3), dtype=np.uint8)
        self.pattern_table_sprite = np.zeros((2, 128, 128, 3), dtype=np.uint8)
        self.scanline = 0
        self.cycle = 0
        self.frame_complete = False
        self.reverse_colors = False

        self.control = PPUControlRegister()  # nmi, ppu m/s, spr height, bg tile sel, inc mode, nametbl sel NN
        self.mask = PPUMaskRegister()  # enh blu, enh grn, enh red, spr en, bg en, spr lft en, bg lft en, gryscale
        self.status = PPUStatusRegister()  # vertical_blank, spr_zero_hit, spr_overflow, 5 unused
        self.vram = LoopyRegister()
        self.tram = LoopyRegister()
        self.fine_x = 0

        self.bg_next_tile_id = 0
        self.bg_next_tile_attrib = 0
        self.bg_next_tile_lsb = 0
        self.bg_next_tile_msb = 0

        self.bg_shifter_pattern_lo = Shifter16Bit()
        self.bg_shifter_pattern_hi = Shifter16Bit()
        self.bg_shifter_attrib_lo = Shifter16Bit()
        self.bg_shifter_attrib_hi = Shifter16Bit()

        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.nmi = False

        self.screen_palette[0x00] = (84, 84, 84)
        self.screen_palette[0x01] = (0, 30, 116) if self.reverse_colors else (116, 30, 0)
        self.screen_palette[0x02] = (8, 16, 144) if self.reverse_colors else (144, 16, 8)
        self.screen_palette[0x03] = (48, 0, 136) if self.reverse_colors else (136, 0, 48)
        self.screen_palette[0x04] = (68, 0, 100) if self.reverse_colors else (100, 0, 68)
        self.screen_palette[0x05] = (92, 0, 48) if self.reverse_colors else (48, 0, 92)
        self.screen_palette[0x06] = (84, 4, 0) if self.reverse_colors else (0, 4, 84)
        self.screen_palette[0x07] = (60, 24, 0) if self.reverse_colors else (0, 24, 60)
        self.screen_palette[0x08] = (32, 42, 0) if self.reverse_colors else (0, 42, 32)
        self.screen_palette[0x09] = (8, 58, 0) if self.reverse_colors else (0, 58, 8)
        self.screen_palette[0x0A] = (0, 64, 0)
        self.screen_palette[0x0B] = (0, 60, 0)
        self.screen_palette[0x0C] = (0, 50, 60) if self.reverse_colors else (60, 50, 0)
        self.screen_palette[0x0D] = (0, 0, 0)
        self.screen_palette[0x0E] = (0, 0, 0)
        self.screen_palette[0x0F] = (0, 0, 0)

        self.screen_palette[0x10] = (152, 150, 152)
        self.screen_palette[0x11] = (8, 76, 196) if self.reverse_colors else (196, 76, 8)
        self.screen_palette[0x12] = (48, 50, 236) if self.reverse_colors else (236, 50, 48)
        self.screen_palette[0x13] = (92, 30, 228) if self.reverse_colors else (228, 30, 92)
        self.screen_palette[0x14] = (136, 20, 176) if self.reverse_colors else (176, 20, 136)
        self.screen_palette[0x15] = (160, 20, 100) if self.reverse_colors else (100, 20, 160)
        self.screen_palette[0x16] = (152, 34, 32) if self.reverse_colors else (32, 34, 152)
        self.screen_palette[0x17] = (120, 60, 0) if self.reverse_colors else (0, 60, 120)
        self.screen_palette[0x18] = (84, 90, 0) if self.reverse_colors else (0, 90, 84)
        self.screen_palette[0x19] = (40, 114, 0) if self.reverse_colors else (0, 114, 40)
        self.screen_palette[0x1A] = (8, 124, 0) if self.reverse_colors else (0, 124, 8)
        self.screen_palette[0x1B] = (0, 118, 40) if self.reverse_colors else (40, 118, 0)
        self.screen_palette[0x1C] = (0, 102, 120) if self.reverse_colors else (120, 102, 0)
        self.screen_palette[0x1D] = (0, 0, 0)
        self.screen_palette[0x1E] = (0, 0, 0)
        self.screen_palette[0x1F] = (0, 0, 0)

        self.screen_palette[0x20] = (236, 238, 236)
        self.screen_palette[0x21] = (76, 154, 236) if self.reverse_colors else (236, 154, 76)
        self.screen_palette[0x22] = (120, 124, 236) if self.reverse_colors else (236, 124, 120)
        self.screen_palette[0x23] = (176, 98, 236) if self.reverse_colors else (236, 98, 176)
        self.screen_palette[0x24] = (228, 84, 236) if self.reverse_colors else (236, 84, 228)
        self.screen_palette[0x25] = (236, 88, 180) if self.reverse_colors else (180, 88, 236)
        self.screen_palette[0x26] = (236, 106, 100) if self.reverse_colors else (100, 106, 236)
        self.screen_palette[0x27] = (212, 136, 32) if self.reverse_colors else (32, 136, 212)
        self.screen_palette[0x28] = (160, 170, 0) if self.reverse_colors else (0, 170, 160)
        self.screen_palette[0x29] = (116, 196, 0) if self.reverse_colors else (0, 196, 116)
        self.screen_palette[0x2A] = (76, 208, 32) if self.reverse_colors else (32, 208, 76)
        self.screen_palette[0x2B] = (56, 204, 108) if self.reverse_colors else (108, 204, 56)
        self.screen_palette[0x2C] = (56, 180, 204) if self.reverse_colors else (204, 180, 56)
        self.screen_palette[0x2D] = (60, 60, 60)
        self.screen_palette[0x2E] = (0, 0, 0)
        self.screen_palette[0x2F] = (0, 0, 0)

        self.screen_palette[0x30] = (236, 238, 236)
        self.screen_palette[0x31] = (168, 204, 236) if self.reverse_colors else (236, 204, 168)
        self.screen_palette[0x32] = (188, 188, 236) if self.reverse_colors else (236, 188, 188)
        self.screen_palette[0x33] = (212, 178, 236) if self.reverse_colors else (236, 178, 212)
        self.screen_palette[0x34] = (236, 174, 236)
        self.screen_palette[0x35] = (236, 174, 212) if self.reverse_colors else (212, 174, 236)
        self.screen_palette[0x36] = (236, 180, 176) if self.reverse_colors else (176, 180, 236)
        self.screen_palette[0x37] = (228, 196, 144) if self.reverse_colors else (144, 196, 228)
        self.screen_palette[0x38] = (204, 210, 120) if self.reverse_colors else (120, 210, 204)
        self.screen_palette[0x39] = (180, 222, 120) if self.reverse_colors else (120, 222, 180)
        self.screen_palette[0x3A] = (168, 226, 144) if self.reverse_colors else (144, 226, 168)
        self.screen_palette[0x3B] = (152, 226, 180) if self.reverse_colors else (180, 226, 152)
        self.screen_palette[0x3C] = (160, 214, 228) if self.reverse_colors else (228, 214, 160)
        self.screen_palette[0x3D] = (160, 162, 160)
        self.screen_palette[0x3E] = (0, 0, 0)
        self.screen_palette[0x3F] = (0, 0, 0)

    def cpu_read(self, addr, _read_only=False):
        data = [0x00]
        if addr == 0x0000:  # control register is not readable
            pass
        elif addr == 0x0001:  # mask register is not readable
            pass
        elif addr == 0x0002:  # status
            data[0] = (self.status.get() & 0xE0) | (self.ppu_data_buffer & 0x1F)
            self.status.set_flag(self.status.Flags.vertical_blank, 0)
            self.address_latch = 0
        elif addr == 0x0003:  # OAM address
            pass
        elif addr == 0x0004:  # OAM data
            pass
        elif addr == 0x0005:  # scroll register is not readable
            pass
        elif addr == 0x0006:  # PPU address is not readable
            pass
        elif addr == 0x0007:  # PPU data
            data[0] = self.ppu_data_buffer
            ppu_address = self.vram.get()
            self.ppu_data_buffer = self.ppu_read(ppu_address)
            if ppu_address >= 0x3F00:
                data[0] = self.ppu_data_buffer
            ppu_address += 32 if self.control.get_flag(self.control.Flags.increment_mode) else 1
            self.vram.set(ppu_address)
        return data[0]

    def cpu_write(self, addr, data):
        if addr == 0x0000:  # control
            self.control.set(data)
            self.tram.set_flag(self.tram.Flags.nametable_x, self.control.get_flag(self.control.Flags.nametable_x))
            self.tram.set_flag(self.tram.Flags.nametable_y, self.control.get_flag(self.control.Flags.nametable_y))
        elif addr == 0x0001:  # mask
            self.mask.set(data)
        elif addr == 0x0002:  # status
            pass
        elif addr == 0x0003:  # OAM address
            pass
        elif addr == 0x0004:  # OAM data
            pass
        elif addr == 0x0005:  # scroll
            if self.address_latch == 0:
                self.fine_x = data & 0x07
                self.tram.set_flag(self.tram.Flags.course_x, data >> 3)
                self.address_latch = 1
            else:
                self.tram.set_flag(self.tram.Flags.fine_y, data & 0x07)
                self.tram.set_flag(self.tram.Flags.course_y, data >> 3)
                self.address_latch = 0
        elif addr == 0x0006:  # PPU address
            if self.address_latch == 0:
                self.tram.set(((data & 0x3F) << 8) | (self.tram.get() & 0x00FF))
                self.address_latch = 1
            else:
                self.tram.set((self.tram.get() & 0xFF00) | data)
                self.vram.set(self.tram.get())
                self.address_latch = 0
        elif addr == 0x0007:  # ppu data
            ppu_address = self.vram.get()
            self.ppu_write(ppu_address, data)
            ppu_address += 32 if self.control.get_flag(self.control.Flags.increment_mode) else 1
            self.vram.set(ppu_address)

    def ppu_read(self, addr, _read_only=False):
        data = [0x00]
        addr &= 0x3FFF
        if self.cart.ppu_read(addr, data):
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            # reading
            data[0] = self.pattern_table[(addr & 0x1000) >> 12][(addr & 0x0FFF)]
        elif 0x2000 <= addr <= 0x3EFF:
            addr &= 0x0FFF

            if self.cart.mirror == self.cart.MIRROR.VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    data[0] = self.name_table[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data[0] = self.name_table[1][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data[0] = self.name_table[0][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data[0] = self.name_table[1][addr & 0x03FF]
            elif self.cart.mirror == self.cart.MIRROR.HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    data[0] = self.name_table[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data[0] = self.name_table[0][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data[0] = self.name_table[1][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data[0] = self.name_table[1][addr & 0x03FF]

        elif 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010:
                addr = 0x0000
            if addr == 0x0014:
                addr = 0x0004
            if addr == 0x0018:
                addr = 0x0008
            if addr == 0x001C:
                addr = 0x000C
            data[0] = self.palette_table[addr]
        # print("ppu read", hex(addr), hex(data[0]))
        return data[0]

    def ppu_write(self, addr, data):
        # print("ppu write", hex(addr), hex(data))
        addr &= 0x3FFF
        if self.cart.ppu_write(addr, data):
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            # writing to pattern table
            self.pattern_table[(addr & 0x0FFF) >> 12][(addr & 0x0FFF)] = data
        elif 0x2000 <= addr <= 0x3EFF:
            # writing to nametables
            addr &= 0x0FFF

            if self.cart.mirror == self.cart.MIRROR.VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    self.name_table[0][addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    self.name_table[1][addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    self.name_table[0][addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    self.name_table[1][addr & 0x03FF] = data
            elif self.cart.mirror == self.cart.MIRROR.HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    self.name_table[0][addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    self.name_table[0][addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    self.name_table[1][addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    self.name_table[1][addr & 0x03FF] = data

        elif 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010:
                addr = 0x0000
            if addr == 0x0014:
                addr = 0x0004
            if addr == 0x0018:
                addr = 0x0008
            if addr == 0x001C:
                addr = 0x000C
            self.palette_table[addr] = data

    def get_screen(self):
        screen = np.array(self.screen_image, dtype=np.uint8)
        return screen

    def get_name_table(self, i, pat):
        for y in range(30):
            for x in range(32):
                t_id = self.name_table[i][(y*32) + x]
                tile_x = (t_id & 0x0f)
                tile_y = ((t_id >> 4) & 0x0f)
                tile = self.get_tile(pat, tile_x, tile_y)
                self.name_table_sprite[i, y*8:(y*8) + 8, x*8:(x*8) + 8] = tile
#        return self.name_table_sprite[i]

    def get_tile(self, tbl_index, tile_x, tile_y):
        offset = tile_y * 256 + tile_x * 16
        tile = np.zeros((8, 8, 3))
        for row in range(8):
            tile_lsb = self.ppu_read(tbl_index * 0x1000 + offset + row + 0x0000)
            tile_msb = self.ppu_read(tbl_index * 0x1000 + offset + row + 0x0008)
            for col in range(8):
                pix = (tile_lsb & 0x01) + (tile_msb & 0x01)
                tile_lsb = tile_lsb >> 1
                tile_msb = tile_msb >> 1
                tile[row, (7 - col)] = self.get_color(self.selected_palette, pix)
        return tile

    def get_pattern_table(self, i, pal):
        for tile_y in range(16):
            for tile_x in range(16):
                offset = tile_y * 256 + tile_x * 16
                for row in range(8):
                    tile_lsb = self.ppu_read(i * 0x1000 + offset + row + 0x0000)
                    tile_msb = self.ppu_read(i * 0x1000 + offset + row + 0x0008)
                    for col in range(8):
                        pix = (tile_lsb & 0x01) + (tile_msb & 0x01)
                        tile_lsb = tile_lsb >> 1
                        tile_msb = tile_msb >> 1
                        self.pattern_table_sprite[i, tile_y * 8 + row, tile_x * 8 + (7 - col)] = self.get_color(pal, pix)

        return self.pattern_table_sprite[i]

    def get_color(self, pal, pix):
        result = self.ppu_read(0x3F00 + (pal << 2) + pix) & 0x3F
        return self.screen_palette[result]

    def clock(self):

        def increment_scroll_x():
            if self.mask.get_flag(self.mask.Flags.render_background) or self.mask.get_flag(self.mask.Flags.render_sprites):
                if self.vram.get_flag(self.vram.Flags.course_x) == 31:
                    self.vram.set_flag(self.vram.Flags.course_x, 0)
                    self.vram.set_flag(self.vram.Flags.nametable_x, 0 if self.vram.get_flag(self.vram.Flags.nametable_x) else 1)
                else:
                    self.vram.set_flag(self.vram.Flags.course_x, self.vram.get_flag(self.vram.Flags.course_x) + 1)

        def increment_scroll_y():
            if self.mask.get_flag(self.mask.Flags.render_background) or self.mask.get_flag(self.mask.Flags.render_sprites):
                if self.vram.get_flag(self.vram.Flags.fine_y) < 7:
                    self.vram.set_flag(self.vram.Flags.fine_y, self.vram.get_flag(self.vram.Flags.fine_y) + 1)
                else:
                    self.vram.set_flag(self.vram.Flags.fine_y, 0)
                    if self.vram.get_flag(self.vram.Flags.course_y) == 29:
                        self.vram.set_flag(self.vram.Flags.course_y, 0)
                        self.vram.set_flag(self.vram.Flags.nametable_y, 0 if self.vram.get_flag(self.vram.Flags.nametable_y) else 1)
                    elif self.vram.get_flag(self.vram.Flags.course_y) == 31:
                        self.vram.set_flag(self.vram.Flags.course_y, 0)
                    else:
                        self.vram.set_flag(self.vram.Flags.course_y, self.vram.get_flag(self.vram.Flags.course_y) + 1)

        def transfer_address_x():
            if self.mask.get_flag(self.mask.Flags.render_background) or self.mask.get_flag(self.mask.Flags.render_sprites):
                self.vram.set_flag(self.vram.Flags.nametable_x, self.tram.get_flag(self.tram.Flags.nametable_x))
                self.vram.set_flag(self.vram.Flags.course_x, self.tram.get_flag(self.tram.Flags.course_x))

        def transfer_address_y():
            if self.mask.get_flag(self.mask.Flags.render_background) or self.mask.get_flag(self.mask.Flags.render_sprites):
                self.vram.set_flag(self.vram.Flags.fine_y, self.tram.get_flag(self.tram.Flags.fine_y))
                self.vram.set_flag(self.vram.Flags.nametable_y, self.tram.get_flag(self.tram.Flags.nametable_y))
                self.vram.set_flag(self.vram.Flags.course_y, self.tram.get_flag(self.tram.Flags.course_y))

        def load_background_shifters():
            self.bg_shifter_pattern_lo.load(self.bg_next_tile_lsb)
            self.bg_shifter_pattern_hi.load(self.bg_next_tile_msb)
            attrib = 0xFF if self.bg_next_tile_attrib & 0b01 else 0x00
            self.bg_shifter_attrib_lo.load(attrib)
            attrib = 0xFF if self.bg_next_tile_attrib & 0b10 else 0x00
            self.bg_shifter_attrib_hi.load(attrib)
            # print("after  loading", self.bg_shifter_pattern_lo.reg)

        def update_shifters():
            if self.mask.get_flag(self.mask.Flags.render_background):
                self.bg_shifter_pattern_lo <<= 1
                self.bg_shifter_pattern_hi <<= 1
                self.bg_shifter_attrib_lo <<= 1
                self.bg_shifter_attrib_hi <<= 1
                # print("after  shifting", self.bg_shifter_pattern_lo.reg)

        if -1 <= self.scanline < 240:
            if self.scanline == 0 and self.cycle == 0:
                self.cycle = 1
            if self.scanline == -1 and self.cycle == 1:
                self.status.set_flag(self.status.Flags.vertical_blank, 0)

            if (2 <= self.cycle < 258) or (321 <= self.cycle < 338):
                update_shifters()

                switch = (self.cycle - 1) % 8
                if switch == 0:
                    load_background_shifters()
                    self.bg_next_tile_id = self.ppu_read(0x2000 | (self.vram.get() & 0x0FFF))
                elif switch == 2:
                    self.bg_next_tile_attrib = self.ppu_read(0x23C0 | (self.vram.get_flag(self.vram.Flags.nametable_y) << 11)
                                                                    | (self.vram.get_flag(self.vram.Flags.nametable_x) << 10)
                                                                    | ((self.vram.get_flag(self.vram.Flags.course_y) >> 2) << 3)
                                                                    | (self.vram.get_flag(self.vram.Flags.course_x) >> 2))
                    if self.vram.get_flag(self.vram.Flags.course_y) & 0x02:
                        self.bg_next_tile_attrib >>= 4
                    if self.vram.get_flag(self.vram.Flags.course_x) & 0x02:
                        self.bg_next_tile_attrib >>= 2
                    self.bg_next_tile_attrib &= 0x03
                elif switch == 4:
                    self.bg_next_tile_lsb = self.ppu_read((self.control.get_flag(self.control.Flags.pattern_background) << 12)
                                                          + (self.bg_next_tile_id << 4)
                                                          + (self.vram.get_flag(self.vram.Flags.fine_y) + 0))
                elif switch == 6:
                    self.bg_next_tile_msb = self.ppu_read((self.control.get_flag(self.control.Flags.pattern_background) << 12)
                                                          + (self.bg_next_tile_id << 4)
                                                          + (self.vram.get_flag(self.vram.Flags.fine_y) + 8))
                elif switch == 7:
                    increment_scroll_x()

            if self.cycle == 256:
                increment_scroll_y()
            if self.cycle == 257:
                load_background_shifters()
                transfer_address_x()
            if self.scanline == -1 and 280 <= self.cycle < 305:
                transfer_address_y()

        if self.scanline == 240:
            pass

        if self.scanline == 241 and self.cycle == 1:
            self.status.set_flag(self.status.Flags.vertical_blank, 1)
            if self.control.get_flag(self.control.Flags.enable_nmi):
                self.nmi = True

        bg_pixel = 0
        bg_palette = 0

        if self.mask.get_flag(self.mask.Flags.render_background):

            p0_pixel = self.bg_shifter_pattern_lo.get(self.fine_x) > 0
            p1_pixel = self.bg_shifter_pattern_hi.get(self.fine_x) > 0
            bg_pixel = (p1_pixel << 1) | p0_pixel

            bg_pal0 = self.bg_shifter_attrib_lo.get(self.fine_x) > 0
            bg_pal1 = self.bg_shifter_attrib_hi.get(self.fine_x) > 0
            bg_palette = (bg_pal1 << 1) | bg_pal0

        if 0 <= self.scanline < 240 and 0 <= self.cycle < 256:
            self.screen_image[self.scanline][self.cycle - 1] = self.get_color(bg_palette, bg_pixel)

        self.cycle += 1

        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.scanline = -1
                self.frame_complete = True
        if self.frame_complete:

            cv2.imshow("screen_image", self.get_screen())
            # self.get_name_table(0, 1)
            # cv2.imshow("nametable", self.name_table_sprite[0])
            # cv2.imshow("pattertable1", self.get_pattern_table(0, self.selected_palette))
            # cv2.imshow("patterntable2", self.get_pattern_table(1, self.selected_palette))
            key = cv2.waitKey(1)
            if key == ord("w"):
                print("pressing up")
                self.bus.controller[0] = 0b1000
            elif key == ord("s"):
                print("pressing down")
                self.bus.controller[0] = 0b100
            elif key == ord("i"):
                print("pressing start")
                self.bus.controller[0] = 0b10000
            else:
                self.bus.controller[0] = 0
            self.frame_complete = False
