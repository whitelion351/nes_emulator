import cv2
from PIL import Image
import numpy as np
from random import choice


class OLC2C02:
    def __init__(self):
        self.bus = None
        self.cart = None
        self.name_table = np.zeros((2, 1024))
        self.palette_table = np.zeros((32,))
        self.pattern_table = np.zeros((2, 4096))
        self.screen_image = None

        self.screen_palette = np.zeros((0x40, 3))
        self.screen_sprite = np.zeros((256, 240))
        self.name_table_sprite = np.zeros((2, 256, 240))
        self.pattern_table_sprite = np.zeros((2, 128, 128))
        self.scanline = 0
        self.cycle = 0
        self.frame_complete = False

        self.screen_palette[0x00] = (84, 84, 84)
        self.screen_palette[0x01] = (0, 30, 116)
        self.screen_palette[0x02] = (8, 16, 144)
        self.screen_palette[0x03] = (48, 0, 136)
        self.screen_palette[0x04] = (68, 0, 100)
        self.screen_palette[0x05] = (92, 0, 48)
        self.screen_palette[0x06] = (84, 4, 0)
        self.screen_palette[0x07] = (60, 24, 0)
        self.screen_palette[0x08] = (32, 42, 0)
        self.screen_palette[0x09] = (8, 58, 0)
        self.screen_palette[0x0A] = (0, 64, 0)
        self.screen_palette[0x0B] = (0, 60, 0)
        self.screen_palette[0x0C] = (0, 50, 60)
        self.screen_palette[0x0D] = (0, 0, 0)
        self.screen_palette[0x0E] = (0, 0, 0)
        self.screen_palette[0x0F] = (0, 0, 0)

        self.screen_palette[0x10] = (152, 150, 152)
        self.screen_palette[0x11] = (8, 76, 196)
        self.screen_palette[0x12] = (48, 50, 236)
        self.screen_palette[0x13] = (92, 30, 228)
        self.screen_palette[0x14] = (136, 20, 176)
        self.screen_palette[0x15] = (160, 20, 100)
        self.screen_palette[0x16] = (152, 34, 32)
        self.screen_palette[0x17] = (120, 60, 0)
        self.screen_palette[0x18] = (84, 90, 0)
        self.screen_palette[0x19] = (40, 114, 0)
        self.screen_palette[0x1A] = (8, 124, 0)
        self.screen_palette[0x1B] = (0, 118, 40)
        self.screen_palette[0x1C] = (0, 102, 120)
        self.screen_palette[0x1D] = (0, 0, 0)
        self.screen_palette[0x1E] = (0, 0, 0)
        self.screen_palette[0x1F] = (0, 0, 0)

        self.screen_palette[0x20] = (236, 238, 236)
        self.screen_palette[0x21] = (76, 154, 236)
        self.screen_palette[0x22] = (120, 124, 236)
        self.screen_palette[0x23] = (176, 98, 236)
        self.screen_palette[0x24] = (228, 84, 236)
        self.screen_palette[0x25] = (236, 88, 180)
        self.screen_palette[0x26] = (236, 106, 100)
        self.screen_palette[0x27] = (212, 136, 32)
        self.screen_palette[0x28] = (160, 170, 0)
        self.screen_palette[0x29] = (116, 196, 0)
        self.screen_palette[0x2A] = (76, 208, 32)
        self.screen_palette[0x2B] = (56, 204, 108)
        self.screen_palette[0x2C] = (56, 180, 204)
        self.screen_palette[0x2D] = (60, 60, 60)
        self.screen_palette[0x2E] = (0, 0, 0)
        self.screen_palette[0x2F] = (0, 0, 0)

        self.screen_palette[0x30] = (236, 238, 236)
        self.screen_palette[0x31] = (168, 204, 236)
        self.screen_palette[0x32] = (188, 188, 236)
        self.screen_palette[0x33] = (212, 178, 236)
        self.screen_palette[0x34] = (236, 174, 236)
        self.screen_palette[0x35] = (236, 174, 212)
        self.screen_palette[0x36] = (236, 180, 176)
        self.screen_palette[0x37] = (228, 196, 144)
        self.screen_palette[0x38] = (204, 210, 120)
        self.screen_palette[0x39] = (180, 222, 120)
        self.screen_palette[0x3A] = (168, 226, 144)
        self.screen_palette[0x3B] = (152, 226, 180)
        self.screen_palette[0x3C] = (160, 214, 228)
        self.screen_palette[0x3D] = (160, 162, 160)
        self.screen_palette[0x3E] = (0, 0, 0)
        self.screen_palette[0x3F] = (0, 0, 0)

    def cpu_read(self, addr, _read_only=False):
        data = 0x0000
        if addr == 0x0000:
            pass
        elif addr == 0x0001:
            pass
        elif addr == 0x0002:
            pass
        elif addr == 0x0003:
            pass
        elif addr == 0x0004:
            pass
        elif addr == 0x0005:
            pass
        elif addr == 0x0006:
            pass
        elif addr == 0x0007:
            pass
        return data

    def cpu_write(self, addr, data):
        if addr == 0x0000:
            pass
        elif addr == 0x0001:
            pass
        elif addr == 0x0002:
            pass
        elif addr == 0x0003:
            pass
        elif addr == 0x0004:
            pass
        elif addr == 0x0005:
            pass
        elif addr == 0x0006:
            pass
        elif addr == 0x0007:
            pass

    def ppu_read(self, addr, _read_only=False):
        data = 0x0000
        addr &= 0x3FFF
        if self.cart.ppu_read(addr, data):
            pass
        return data

    def ppu_write(self, addr, data):
        addr &= 0x3FFF
        if self.cart.ppu_write(addr, data):
            pass

    def get_screen(self):
        return self.screen_image

    def get_name_table(self, i):
        return self.name_table_sprite[i]

    def get_pattern_table(self, i):
        return self.pattern_table_sprite[i]

    def clock(self):
        x = self.cycle if self.cycle < 255 else 255
        y = self.scanline if self.scanline < 239 else 239
        self.screen_sprite[x, y] = choice([0.0, 1.0])

        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.scanline = -1
                self.frame_complete = True
