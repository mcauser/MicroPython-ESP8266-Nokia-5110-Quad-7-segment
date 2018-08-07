# Emulating a TM1637 quad 7-segment display module on a Nokia 5110 display

# WeMos D1 Mini -- Nokia 5110 PCD8544 LCD
# D3 (GPIO0) ----- 0 RST
# D4 (GPIO2) ----- 1 CE
# D8 (GPIO15) ---- 2 DC
# D7 (GPIO13) ---- 3 Din
# D5 (GPIO14) ---- 4 Clk
# 3V3 ------------ 5 Vcc
# D6 (GPIO12) ---- 6 BL
# G -------------- 7 Gnd

from machine import Pin, SPI
import time
import pcd8544
import nokia7seg

spi = SPI(1)
spi.init(baudrate=8000000, polarity=0, phase=0)
cs = Pin(2)
dc = Pin(15)
rst = Pin(0)

# backlight on
bl = Pin(12, Pin.OUT, value=1)

lcd = pcd8544.PCD8544(spi, cs, dc, rst)
display = nokia7seg.Nokia7Seg(lcd)

# all LEDS on "8.8.:8.8."
display.write([255, 255, 255, 255])
display.colon(True)

# all LEDS off
display.write([0, 0, 0, 0])

# display "3.145"
display.write([207, 6, 102, 109])

# display "0123"
display.write([63, 6, 91, 79])
display.write(bytearray([63, 6, 91, 79]))

# display "4567"
display.write([102, 109, 125, 7])

# set middle two segments to "12", "4127"
display.write([6, 91], 1)

# set last segment to "9", "4129"
display.write([111], 3)

# walk through all possible LED combinations
for i in range(255):
	display.write([i, i | 0x80, i, i])

# show "AbCd"
display.write([119, 124, 57, 94])
display.show('abcd')

# show "COOL"
display.write([0b00111001, 0b00111111, 0b00111111, 0b00111000])
display.show('cool')

# converts a digit 0-0x0f to a byte representing a single segment
# use write() to render the byte on a single segment
display.encode_digit(0)
# 63

display.encode_digit(8)
# 127

display.encode_digit(0x0f)
# 113

# 15 or 0x0f generates a segment that can output a F character
display.encode_digit(15)
# 113

display.encode_digit(0x0f)
# 113

# used to convert a 1-4 length string to an array of segments
display.encode_string('   1')
# bytearray(b'\x00\x00\x00\x06')

display.encode_string('2   ')
# bytearray(b'[\x00\x00\x00')

display.encode_string('1234')
# bytearray(b'\x06[Of')

display.encode_string('-12-')
# bytearray(b'@\x06[@')

display.encode_string('cafe')
# bytearray(b'9wqy')

display.encode_string('CAFE')
# bytearray(b'9wqy')

display.encode_string('a')
# bytearray(b'w\x00\x00\x00')

display.encode_string('ab')
# bytearray(b'w|\x00\x00')

# used to convert a single character to a segment byte
display.encode_char('1')
# 6

display.encode_char('9')
# 111

display.encode_char('-')
# 64

display.encode_char('a')
# 119

display.encode_char('F')
# 113

# display "dEAd", "bEEF", "CAFE" and "bAbE"
display.hex(0xdead)
display.hex(0xbeef)
display.hex(0xcafe)
display.hex(0xbabe)

# show "  FF" (hex right aligned)
display.hex(0xff)

# show "   1" (numbers right aligned)
display.number(1)

# show "  12"
display.number(12)

# show " 123"
display.number(123)

# show "9999" capped at 9999
display.number(20000)

# show "  -1"
display.number(-1)

# show " -12"
display.number(-12)

# show "-123"
display.number(-123)

# show "-999" capped at -999
display.number(-1234)

# show "01:02"
display.numbers(1,2)

# show "-5:11"
display.numbers(-5,11)

# show "12:59"
display.numbers(12,59)

# Show Help
display.show('Help')
display.write(display.encode_string('Help'))

# Scroll Hello World from right to left
display.scroll('Hello World') # 4 fps
display.scroll('Hello World', 1000) # 1 fps

# Scroll all available characters
display.scroll(list(nokia7seg._SEGMENTS))

# show temperature '24*C'
display.temperature(24)
display.show('24*C')
