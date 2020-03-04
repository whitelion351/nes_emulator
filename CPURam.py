class CPURam:
    def __init__(self):
        self.bus = None
        self.size = 2048
        self.ram = [0x00 for _ in range(self.size)]
