from machine import SPI, Pin
import st7789

# FUENTES DISPONIBLES
# import vga1_8x8 as font
# import vga2_8x8 as font
#import vga1_8x16 as font           
# import vga2_8x16 as font
# import vga1_16x16 as font
# import vga2_16x16 as font
# import vga1_bold_16x16 as font
# import vga2_bold_16x16 as font
import vga1_16x32 as font1
# import vga2_16x32 as font 
import vga1_bold_16x32 as font2
# import vga2_bold_16x32 as font

class Display:
    def __init__(self, sck, mosi, miso, reset, dc, cs, backlight, id = 0, baudrate = 30000000, polarity = 0, phase = 0, bits = 8, firstbit = 0):
        self.tft = st7789.ST7789(SPI(id, baudrate = baudrate, polarity = polarity, phase = phase, bits = bits, firstbit = firstbit, sck = Pin(sck), 
                    mosi = Pin(mosi), miso = Pin(miso)), 240, 320, reset = Pin(reset, Pin.OUT), dc = Pin(dc, Pin.OUT), cs = Pin(cs, Pin.OUT), 
                    backlight = Pin(backlight, Pin.OUT), rotation = 0)
        
        self.tft.init()
    
    def data_discrete(self, x, y, r, g, b, label, value, width = 210, height = 50):
        self.tft.fill_rect(x, y, width, height, st7789.color565(r, g, b))
        self.tft.text(font1, label, x+1, y+1, st7789.WHITE)
        self.tft.text(font2, value, x+50, y+1, st7789.WHITE)


    def data_logic(self, x, y, label, state, width = 30, height = 43):
        if state == 1:
            self.tft.fill_rect(x, y, width, height, st7789.GREEN)
        else:
            self.tft.fill_rect(x, y, width, height, st7789.RED)
        
        self.tft.text(font2, label, x+1, y+1, st7789.WHITE)

    def error(self, x, y, error):
        self.tft.fill(st7789.BLACK)
        self.tft.text(font2, error, x, y, st7789.RED)