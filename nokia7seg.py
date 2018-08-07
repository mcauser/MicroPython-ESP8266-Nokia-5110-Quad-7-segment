"""
MicroPython Nokia 5110 7-segment PCD8544 84x48 LCD driver
https://github.com/mcauser/MicroPython-ESP8266-Nokia-5110-Quad-7-segment

MIT License
Copyright (c) 2016 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Emulating a TM1637 quad 7-segment display module on a Nokia 5110 display

import framebuf
from time import sleep_ms

# 0-9, a-z, blank, dash, star
_SEGMENTS = bytearray(b'\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\x77\x7C\x39\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\x73\x67\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63')

class Nokia7Seg:
	def __init__(self,lcd):
		self.lcd = lcd
		self.buf = bytearray((lcd.height // 8) * lcd.width)
		self.fbuf = framebuf.FrameBuffer(self.buf, lcd.width, lcd.height, framebuf.MVLSB)
		self.pos = 0
		self.clear()

	def _write_byte(self, b):
		x = self.pos * 21
		if self.pos >= 2:
		  x += 2
		y = 12
		# a segment
		self.fbuf.hline(x+1, y+0, 14, (b & 0x01))
		self.fbuf.hline(x+2, y+1, 12, (b & 0x01))
		self.fbuf.hline(x+3, y+2, 10, (b & 0x01))
		# b segment
		self.fbuf.vline(x+13, y+3, 8, (b & 0x02))
		self.fbuf.vline(x+14, y+2, 10, (b & 0x02))
		self.fbuf.vline(x+15, y+1, 10, (b & 0x02))
		# c segment
		self.fbuf.vline(x+13, y+14, 8, (b & 0x04))
		self.fbuf.vline(x+14, y+13, 10, (b & 0x04))
		self.fbuf.vline(x+15, y+14, 10, (b & 0x04))
		# d segment
		self.fbuf.hline(x+3, y+22, 10, (b & 0x08))
		self.fbuf.hline(x+2, y+23, 12, (b & 0x08))
		self.fbuf.hline(x+1, y+24, 14, (b & 0x08))
		# e segment
		self.fbuf.vline(x+0, y+14, 10, (b & 0x10))
		self.fbuf.vline(x+1, y+13, 10, (b & 0x10))
		self.fbuf.vline(x+2, y+14, 8, (b & 0x10))
		# f segment
		self.fbuf.vline(x+0, y+1, 10, (b & 0x20))
		self.fbuf.vline(x+1, y+2, 10, (b & 0x20))
		self.fbuf.vline(x+2, y+3, 8, (b & 0x20))
		# g segment
		self.fbuf.hline(x+3, y+11, 10, (b & 0x40))
		self.fbuf.hline(x+2, y+12, 12, (b & 0x40))
		self.fbuf.hline(x+3, y+13, 10, (b & 0x40))
		# dot segment
		self.fbuf.fill_rect(x+17, y+23, 2, 2, (b & 0x80))
		self.pos += 1
		self._draw()

	def _draw(self):
		self.lcd.data(self.buf)

	def clear(self, color=0):
		"""Fill the display with off pixels"""
		self.fbuf.fill(color)
		self._draw()

	def colon(self, on=True):
		"""Display a colon between the 2nd and 3rd segments"""
		# colon top square
		self.fbuf.fill_rect(40, 19, 2, 2, (1 if on else 0))
		# colon bottom square
		self.fbuf.fill_rect(40, 28, 2, 2, (1 if on else 0))
		self._draw()

	def write(self, segments, pos=0):
		"""Display up to 4 segments moving right from a given position.
		The MSB in the 2nd segment controls the colon between the 2nd
		and 3rd segments."""
		if not 0 <= pos <= 3:
			raise ValueError("Position out of range")

		self.pos = pos

		for seg in segments:
			self._write_byte(seg)

	def encode_digit(self, digit):
		"""Convert a character 0-9, a-f to a segment."""
		return _SEGMENTS[digit & 0x0f]

	def encode_string(self, string):
		"""Convert an up to 4 character length string containing 0-9, a-z,
		space, dash, star to an array of segments, matching the length of the
		source string."""
		segments = bytearray(len(string))
		for i in range(len(string)):
			segments[i] = self.encode_char(string[i])
		return segments

	def encode_char(self, char):
		"""Convert a character 0-9, a-z, space, dash or star to a segment."""
		o = ord(char)
		if o == 32:
			return _SEGMENTS[36] # space
		if o == 42:
			return _SEGMENTS[38] # star/degrees
		if o == 45:
			return _SEGMENTS[37] # dash
		if o >= 65 and o <= 90:
			return _SEGMENTS[o-55] # uppercase A-Z
		if o >= 97 and o <= 122:
			return _SEGMENTS[o-87] # lowercase a-z
		if o >= 48 and o <= 57:
			return _SEGMENTS[o-48] # 0-9
		raise ValueError("Character out of range: {:d} '{:s}'".format(o, chr(o)))

	def hex(self, val):
		"""Display a hex value 0x0000 through 0xffff, right aligned."""
		string = '{:04x}'.format(val & 0xffff)
		self.write(self.encode_string(string))

	def number(self, num):
		"""Display a numeric value -999 through 9999, right aligned."""
		# limit to range -999 to 9999
		num = max(-999, min(num, 9999))
		string = '{0: >4d}'.format(num)
		self.write(self.encode_string(string))

	def numbers(self, num1, num2, colon=True):
		"""Display two numeric values -9 through 99, with leading zeros
		and separated by a colon."""
		num1 = max(-9, min(num1, 99))
		num2 = max(-9, min(num2, 99))
		segments = self.encode_string('{0:0>2d}{1:0>2d}'.format(num1, num2))
		self.write(segments)
		self.colon(colon)

	def temperature(self, num):
		if num < -9:
			self.show('lo') # low
		elif num > 99:
			self.show('hi') # high
		else:
			string = '{0: >2d}'.format(num)
			self.write(self.encode_string(string))
		self.write([_SEGMENTS[38], _SEGMENTS[12]], 2) # degrees C

	def show(self, string, colon=False):
		segments = self.encode_string(string)
		self.write(segments[:4])
		self.colon(colon)

	def scroll(self, string, delay=250):
		segments = string if isinstance(string, list) else self.encode_string(string)
		data = [0] * 8
		data[4:0] = list(segments)
		for i in range(len(segments) + 5):
			self.write(data[0+i:4+i])
			sleep_ms(delay)
