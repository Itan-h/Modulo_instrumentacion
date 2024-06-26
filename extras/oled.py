from machine import SPI, Pin
import st7789

# FUENTES DISPONIBLES
# import vga1_8x8 as font
#import vga2_8x8 as font3
# import vga1_8x16 as font           
# import vga2_8x16 as font
# import vga1_16x16 as font
import vga2_16x16 as font3
# import vga1_bold_16x16 as font
# import vga2_bold_16x16 as font
import vga1_16x32 as font1
# import vga2_16x32 as font 
import vga1_bold_16x32 as font2
# import vga2_bold_16x32 as font

class Display():
    def __init__(self, sck, mosi, miso=None, reset=None, dc=None, backlight=None, cs=None,id = 2, baudrate = 30000000, polarity = 1, phase = 1, bits = 8, firstbit = 0):
        self.tft = st7789.ST7789(SPI(id, baudrate = baudrate, polarity = polarity, phase = phase, bits = bits, firstbit = firstbit, sck=sck, mosi = mosi, miso=miso),
                    240, 320, dc = dc, reset = reset,
                    cs = cs, rotation = 1)
        
        self.tft.init()
    
    def data_discrete(self, x, y,label, value, unit=" ", bg=st7789.BLACK):
        self.tft.text(font1, " "+label+ f"{value} "+unit, x, y, st7789.WHITE, bg)

    def data_logic(self, x, y, label, state):
        if state == 1:
            self.tft.text(font2, " "+label+" ", x+1, y+1, st7789.WHITE,st7789.color565(2, 186, 51))
        else:
            self.tft.text(font2, " "+label+" ", x+1, y+1, st7789.WHITE,st7789.RED)
    def graph(self, x1, y1, x2, y2, color=st7789.BLUE):
            self.tft.line(x1,y1,x2,y2,color)
            
    def oled_clear(self):
        self.tft.fill(st7789.BLACK)
        
    def label(self, x, y, label, color=st7789.WHITE):
        self.tft.text(font3,label ,x ,y ,color)

    def error(self, x, y, error):
        self.tft.fill(st7789.BLACK)
        self.tft.text(font2, error, x, y, st7789.RED, st7789.BLACK)