import framebuf

# 0-9, a-f, blank, dash
_SEGMENTS = [63,6,91,79,102,109,125,7,127,111,119,124,57,94,121,113,0,64]

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
		The MSB is the decimal point."""
		if not 0 <= pos <= 3:
			raise ValueError("Position out of range")

		self.pos = pos

		for seg in segments:
			self._write_byte(seg)

	def encode_digit(self, digit):
		"""Convert a character 0-9, a-f to a segment."""
		return _SEGMENTS[digit & 0x0f]

	def encode_string(self, string):
		"""Convert an up to 4 character length string containing 0-9, a-f,
		space, dash to an array of segments, matching the length of the
		source string."""
		segments = bytearray(4)
		for i in range(0, min(4, len(string))):
			segments[i] = self.encode_char(string[i])
		return segments

	def encode_char(self, char):
		"""Convert a character 0-9, a-f, space or dash to a segment."""
		o = ord(char)
		# space
		if o == 32:
			return _SEGMENTS[16]
		# dash
		if o == 45:
			return _SEGMENTS[17]
		# uppercase A-F
		if o >= 65 and o <= 70:
			return _SEGMENTS[o-55]
		# lowercase a-f
		if o >= 97 and o <= 102:
			return _SEGMENTS[o-87]
		# 0-9
		if o >= 48 and o <= 57:
			return _SEGMENTS[o-48]
		raise ValueError("Character out of range")

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
