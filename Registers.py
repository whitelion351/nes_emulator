from enum import Enum


class LoopyRegister:
    class Flags(Enum):
        unused = 0b1 << 15
        fine_y = 0b111 << 12
        nametable_y = 0b1 << 11
        nametable_x = 0b1 << 10
        course_y = 0b11111 << 5
        course_x = 0b11111 << 0

    def __init__(self, init_value=None):
        self.reg = 0x0000 if init_value is None else init_value

    def set_flag(self, f, v):
        if f == self.Flags.unused:
            self.reg = (self.reg & ~self.Flags.unused.value) | (v << 15)
        if f == self.Flags.fine_y:
            self.reg = (self.reg & ~self.Flags.fine_y.value) | (v << 12)
        if f == self.Flags.nametable_y:
            self.reg = (self.reg & ~self.Flags.nametable_y.value) | (v << 11)
        if f == self.Flags.nametable_x:
            self.reg = (self.reg & ~self.Flags.nametable_x.value) | (v << 10)
        if f == self.Flags.course_y:
            self.reg = (self.reg & ~self.Flags.course_y.value) | (v << 5)
        if f == self.Flags.course_x:
            self.reg = (self.reg & ~self.Flags.course_x.value) | (v << 0)

    def get_flag(self, f):
        if f == self.Flags.unused:
            return (self.reg & self.Flags.unused.value) >> 15
        if f == self.Flags.fine_y:
            return (self.reg & self.Flags.fine_y.value) >> 12
        if f == self.Flags.nametable_y:
            return (self.reg & self.Flags.nametable_y.value) >> 11
        if f == self.Flags.nametable_x:
            return (self.reg & self.Flags.nametable_x.value) >> 10
        if f == self.Flags.course_y:
            return (self.reg & self.Flags.course_y.value) >> 5
        if f == self.Flags.course_x:
            return (self.reg & self.Flags.course_x.value) >> 0

    def set(self, v):
        self.reg = v

    def get(self):
        return self.reg


class PPUStatusRegister:
    class Flags(Enum):
        vertical_blank = 1 << 7
        sprite_zero_hit = 1 << 6
        sprite_overflow = 1 << 5
        unused = 0b11111 << 0

    def __init__(self, init_value=None):
        self.reg = 0x0000 if init_value is None else init_value

    def set_flag(self, f, v):
        if f == self.Flags.vertical_blank:
            self.reg = (self.reg & ~self.Flags.vertical_blank.value) | (v << 7)
        if f == self.Flags.sprite_zero_hit:
            self.reg = (self.reg & ~self.Flags.sprite_zero_hit.value) | (v << 6)
        if f == self.Flags.sprite_overflow:
            self.reg = (self.reg & ~self.Flags.sprite_overflow.value) | (v << 5)
        if f == self.Flags.unused:
            self.reg = (self.reg & ~self.Flags.unused.value) | (v << 0)

    def get_flag(self, f):
        if f == self.Flags.vertical_blank:
            return (self.reg & self.Flags.vertical_blank.value) >> 7
        if f == self.Flags.sprite_zero_hit:
            return (self.reg & self.Flags.sprite_zero_hit.value) >> 6
        if f == self.Flags.sprite_overflow:
            return (self.reg & self.Flags.sprite_overflow.value) >> 5
        if f == self.Flags.unused:
            return (self.reg & self.Flags.unused.value) >> 0

    def set(self, v):
        self.reg = v

    def get(self):
        return self.reg


class PPUControlRegister:
    class Flags(Enum):
        enable_nmi = 1 << 7
        slave_mode = 1 << 6
        sprite_size = 1 << 5
        pattern_background = 1 << 4
        pattern_sprite = 1 << 3
        increment_mode = 1 << 2
        nametable_y = 1 << 1
        nametable_x = 1 << 0

    def __init__(self, init_value=None):
        self.reg = 0x0000 if init_value is None else init_value

    def set_flag(self, f, v):
        if f == self.Flags.enable_nmi:
            self.reg = (self.reg & ~self.Flags.enable_nmi.value) | (v << 7)
        if f == self.Flags.slave_mode:
            self.reg = (self.reg & ~self.Flags.slave_mode.value) | (v << 6)
        if f == self.Flags.sprite_size:
            self.reg = (self.reg & ~self.Flags.sprite_size.value) | (v << 5)
        if f == self.Flags.pattern_background:
            self.reg = (self.reg & ~self.Flags.pattern_background.value) | (v << 4)
        if f == self.Flags.pattern_sprite:
            self.reg = (self.reg & ~self.Flags.pattern_sprite.value) | (v << 3)
        if f == self.Flags.increment_mode:
            self.reg = (self.reg & ~self.Flags.increment_mode.value) | (v << 2)
        if f == self.Flags.nametable_y:
            self.reg = (self.reg & ~self.Flags.nametable_y.value) | (v << 1)
        if f == self.Flags.nametable_x:
            self.reg = (self.reg & ~self.Flags.nametable_x.value) | (v << 0)

    def get_flag(self, f):
        if f == self.Flags.enable_nmi:
            return (self.reg & self.Flags.enable_nmi.value) >> 7
        if f == self.Flags.slave_mode:
            return (self.reg & self.Flags.slave_mode.value) >> 6
        if f == self.Flags.sprite_size:
            return (self.reg & self.Flags.sprite_size.value) >> 5
        if f == self.Flags.pattern_background:
            return (self.reg & self.Flags.pattern_background.value) >> 4
        if f == self.Flags.pattern_sprite:
            return (self.reg & self.Flags.pattern_sprite.value) >> 3
        if f == self.Flags.increment_mode:
            return (self.reg & self.Flags.increment_mode.value) >> 2
        if f == self.Flags.nametable_y:
            return (self.reg & self.Flags.nametable_y.value) >> 1
        if f == self.Flags.nametable_x:
            return (self.reg & self.Flags.nametable_x.value) >> 0

    def set(self, v):
        self.reg = v

    def get(self):
        return self.reg


class PPUMaskRegister:
    class Flags(Enum):
        enhance_blue = 1 << 7
        enhance_green = 1 << 6
        enhance_red = 1 << 5
        render_sprites = 1 << 4
        render_background = 1 << 3
        render_sprites_left = 1 << 2
        render_background_left = 1 << 1
        grayscale = 1 << 0

    def __init__(self, init_value=None):
        self.reg = 0x0000 if init_value is None else init_value

    def set_flag(self, f, v):
        if f == self.Flags.enhance_blue:
            self.reg = (self.reg & ~self.Flags.enhance_blue.value) | (v << 7)
        if f == self.Flags.enhance_green:
            self.reg = (self.reg & ~self.Flags.enhance_green.value) | (v << 6)
        if f == self.Flags.enhance_red:
            self.reg = (self.reg & ~self.Flags.enhance_red.value) | (v << 5)
        if f == self.Flags.render_sprites:
            self.reg = (self.reg & ~self.Flags.render_sprites.value) | (v << 4)
        if f == self.Flags.render_background:
            self.reg = (self.reg & ~self.Flags.render_background.value) | (v << 3)
        if f == self.Flags.render_sprites_left:
            self.reg = (self.reg & ~self.Flags.render_sprites_left.value) | (v << 2)
        if f == self.Flags.render_background_left:
            self.reg = (self.reg & ~self.Flags.render_background_left.value) | (v << 1)
        if f == self.Flags.grayscale:
            self.reg = (self.reg & ~self.Flags.grayscale.value) | (v << 0)

    def get_flag(self, f):
        if f == self.Flags.enhance_blue:
            return (self.reg & self.Flags.enhance_blue.value) >> 7
        if f == self.Flags.enhance_green:
            return (self.reg & self.Flags.enhance_green.value) >> 6
        if f == self.Flags.enhance_red:
            return (self.reg & self.Flags.enhance_red.value) >> 5
        if f == self.Flags.render_sprites:
            return (self.reg & self.Flags.render_sprites.value) >> 4
        if f == self.Flags.render_background:
            return (self.reg & self.Flags.render_background.value) >> 3
        if f == self.Flags.render_sprites_left:
            return (self.reg & self.Flags.render_sprites_left.value) >> 2
        if f == self.Flags.render_background_left:
            return (self.reg & self.Flags.render_background_left.value) >> 1
        if f == self.Flags.grayscale:
            return (self.reg & self.Flags.grayscale.value) >> 0

    def set(self, v):
        self.reg = v

    def get(self):
        return self.reg


class Shifter16Bit:
    def __init__(self):
        self.reg = [0 for _ in range(16)]

    def __lshift__(self, other):
        del self.reg[0:other]
        return self

    def load(self, data):
        data = bin(data)[2:]
        # print("data to load", data)
        padding = 8 - len(data)
        to_add = [0 for _ in range(padding)]
        for i in data:
            to_add.append(int(i))
        # print("data after padding", to_add)
        self.reg[8:16] = to_add
        # print("reg final", self.reg)

    def get(self, v):
        return self.reg[v]
