from time import sleep
from Bus import Bus as Nes


nes = Nes()
# nes.insert_cart("nestest.nes")
# nes.insert_cart("Donkey Kong Jr. (JU) [p1].nes")
# nes.insert_cart("Bomberman (U).nes")
nes.insert_cart("Burger Time (U) [!].nes")
# nes.insert_cart("Super Mario Bros (E).nes")
# nes.insert_cart("Mario Bros (JU).nes")
# nes.insert_cart("Donkey Kong (JU) [p1].nes")
nes.reset()
# nes.cpu.pc = 0xC000

# nes.cart.PRG_memory[0x00: 0x0A] = [0xea, 0x20, 0x08, 0x80, 0x4c, 0x02, 0x40, 0x0ea, 0x60, 0xea, 0xea]
# nes.cpu.pc = 0x8000
while not nes.please_break:
    nes.clock()
    if nes.please_break:
        print("error reading or writing detected")
    sleep(0.0)
