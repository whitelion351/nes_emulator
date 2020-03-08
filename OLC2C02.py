import cv2
import numpy as np
from time import sleep

class OLC2C02:
    def __init__(self):

        self.my_temp = 1
        self.bus = None
        self.cart = None
        self.name_table = np.zeros((2, 1024), dtype=np.uint8)
        self.palette_table = np.zeros((32,), dtype=np.uint8)
        self.pattern_table = np.zeros((2, 4096), dtype=np.uint8)
        self.screen_size_x = 256
        self.screen_size_y = 240
        self.screen_image = np.zeros((256, 240, 3), dtype=np.uint8)

        self.selected_palette = 0
        self.screen_palette = np.zeros((0x40, 3), dtype=np.uint8)
        self.screen_sprite = np.zeros((341, 261, 3), dtype=np.uint8)
        self.name_table_sprite = np.zeros((2, 240, 256, 3), dtype=np.uint8)
        self.pattern_table_sprite = np.zeros((2, 128, 128, 3), dtype=np.uint8)
        self.scanline = 0
        self.cycle = 0
        self.frame_complete = False
        self.reverse_colors = False

        self.control = self.PPURegister(init_value=0)  # nmi, ppu m/s, spr height, bg tile sel, inc mode, nametbl sel NN
        self.mask = self.PPURegister(init_value=0)  # em blu, em grn, em red, spr en, bg en, spr lft en, bg lft en, gryscale
        self.status = self.PPURegister(init_value=0)  # vertical_blank, spr_zero_hit, spr_overflow, 5 unused

        self.nmi = False
        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.ppu_address = 0x0000

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

    class PPURegister:
        def __init__(self, init_value=None):
            self.value = 0x00 if init_value is None else init_value

        def set_flag(self, f, v):
            if f == "vertical_blank" or f == "enhance_blue" or f == "enable_nmi":
                f = 1 << 7
            elif f == "sprite_zero_hit" or f == "enhance_green" or f == "slave_mode":
                f = 1 << 6
            elif f == "sprite_overflow" or f == "enhance_red" or f == "sprite_size":
                f = 1 << 5
            elif f == "render_sprites" or f == "pattern_background":
                f = 1 << 4
            elif f == "render_background" or f == "pattern_sprite":
                f = 1 << 3
            elif f == "render_sprites_left" or f == "increment_mode":
                f = 1 << 2
            elif f == "render_background_left" or f == "name_table_y":
                f = 1 << 1
            elif f == "grayscale" or f == "name_table_x":
                f = 1 << 0
            else:
                print(f, "bit not found in register")
                return

            if v:
                self.value |= f
            else:
                self.value &= ~f

        def get_flag(self, f):
            if f == "vertical_blank" or f == "enhance_blue" or f == "enable_nmi":
                f = 1 << 7
            elif f == "sprite_zero_hit" or f == "enhance_green" or f == "slave_mode":
                f = 1 << 6
            elif f == "sprite_overflow" or f == "enhance_red" or f == "sprite_size":
                f = 1 << 5
            elif f == "render_sprites" or f == "pattern_background":
                f = 1 << 4
            elif f == "render_background" or f == "pattern_sprite":
                f = 1 << 3
            elif f == "render_sprites_left" or f == "increment_mode":
                f = 1 << 2
            elif f == "render_background_left" or f == "name_table_y":
                f = 1 << 1
            elif f == "grayscale" or f == "name_table_x":
                f = 1 << 0
            else:
                print(f, "bit not found in register")
                return 0

            if self.value & f > 0:
                return 1
            else:
                return 0

    def cpu_read(self, addr, _read_only=False):
        data = [0x00]
        if addr == 0x0000:  # control register is not readable
            pass
        elif addr == 0x0001:  # mask register is not readable
            pass
        elif addr == 0x0002:  # status
            data[0] = (self.status.value & 0xE0) | (self.ppu_data_buffer & 0x1F)
            self.status.set_flag("vertical_blank", 0)
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
            self.ppu_data_buffer = self.ppu_read(self.ppu_address)
            if self.ppu_address >= 0x3F00:
                data[0] = self.ppu_data_buffer
            self.ppu_address += 32 if self.control.get_flag("increment_mode") else 1
            # print("cpu_read from ppu_address", hex(self.ppu_address))
        return data[0]

    def cpu_write(self, addr, data):
        if addr == 0x0000:  # control
            self.control.value = data
        elif addr == 0x0001:  # mask
            self.mask.value = data
        elif addr == 0x0002:  # status
            pass
        elif addr == 0x0003:  # OAM address
            pass
        elif addr == 0x0004:  # OAM data
            pass
        elif addr == 0x0005:  # scroll
            pass
        elif addr == 0x0006:  # PPU address
            if self.address_latch == 0:
                self.ppu_address = ((data & 0x3F) << 8) | (self.ppu_address & 0x00FF)
                self.address_latch = 1
            else:
                self.ppu_address = (self.ppu_address & 0xFF00) | data
                self.address_latch = 0
        elif addr == 0x0007:  # ppu data
            self.ppu_write(self.ppu_address, data)
            self.ppu_address += 32 if self.control.get_flag("increment_mode") else 1
            # print("cpu_write to ppu_address", hex(self.ppu_address), hex(data))

    def ppu_read(self, addr, _read_only=False):
        data = [0x00]
        addr &= 0x3FFF
        if self.cart.ppu_read(addr, data):
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            # reading
            data[0] = self.pattern_table[(addr & 0x1000) >> 12, (addr & 0x0FFF)]
        elif 0x2000 <= addr <= 0x3EFF:
            addr &= 0x0FFF

            if self.cart.mirror == self.cart.MIRROR.VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    data[0] = self.name_table[0, addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data[0] = self.name_table[1, addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data[0] = self.name_table[0, addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data[0] = self.name_table[1, addr & 0x03FF]
            elif self.cart.mirror == self.cart.MIRROR.HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    data[0] = self.name_table[0, addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data[0] = self.name_table[0, addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data[0] = self.name_table[1, addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data[0] = self.name_table[1, addr & 0x03FF]

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
            self.pattern_table[(addr & 0x0FFF) >> 12, (addr & 0x0FFF)] = data
        elif 0x2000 <= addr <= 0x3EFF:
            # writing to nametables
            addr &= 0x0FFF

            if self.cart.mirror == self.cart.MIRROR.VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    self.name_table[0, addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    self.name_table[1, addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    self.name_table[0, addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    self.name_table[1, addr & 0x03FF] = data
            elif self.cart.mirror == self.cart.MIRROR.HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    print("nametable 0 [{}]".format(addr & 0x03FF))
                    self.name_table[0, addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    print("nametable 0 [{}]".format(addr & 0x03FF))
                    self.name_table[0, addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    print("nametable 1 [{}]".format(addr & 0x03FF))
                    self.name_table[1, addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    print("nametable 1 [{}]".format(addr & 0x03FF))
                    self.name_table[1, addr & 0x03FF] = data

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
        return self.screen_image

    def get_name_table(self, i):
        for y in range(30):
            # print([hex(v) for v in self.name_table[i][y*32:y*32 + 32]])
            for x in range(32):
                t_id = self.name_table[i, (y*32) + x]
                tile_x = (t_id & 0x0f)
                tile_y = ((t_id >> 4) & 0x0f)
                # print("nm_tbl x: {} nm_tbl y: {} tile x: {} tile y: {}".format(x, y, tile_x, tile_y))
                # tile = self.pattern_table_sprite[1, tile_y:tile_y + 8, tile_x:tile_x + 8]
                tile = self.get_tile(1, tile_x, tile_y)
                self.name_table_sprite[i, y*8:(y*8) + 8, x*8:(x*8) + 8] = tile
        # print()
        return self.name_table_sprite[i]

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
        if self.scanline == -1 and self.cycle == 1:
            self.status.set_flag("vertical_blank", 0)

        if self.scanline == 241 and self.cycle == 1:
            self.status.set_flag("vertical_blank", 1)
            if self.control.get_flag("enable_nmi"):
                self.nmi = True

        self.cycle += 1

        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.scanline = -1
                self.frame_complete = True
        if self.frame_complete:
            cv2.imshow("nametable0", self.get_name_table(0))
            # cv2.imshow("nametable1", self.get_name_table(1))
            if self.my_temp:
                cv2.imshow("pattab1", self.get_pattern_table(1, self.selected_palette))
                # cv2.imshow("pattab2", self.get_pattern_table(1, self.selected_palette))
            key = cv2.waitKey(1)
            if key == ord("b"):
                sleep(600)
            elif key == ord("n"):
                self.my_temp = 0
            self.frame_complete = False
