

class Framework():
	def __init__(self, boxes, img_size=None):
		self.rows = self.orgnize_boxes(boxes)
		self.boxes = []
		k = 0
		for i, row in enumerate(self.rows):
			for j, box in enumerate(row):
				box['pos'] = (i, j)
				box['index'] = k
				self.rows[i][j] = box
				self.boxes.append(box)
				k += 1
		self.cache = {}
		self.imsize = img_size
	def find_next_n(self, box, n):
		m, n = box['pos']
		boxes = []
		num = 0
		end = False
		for i, row in enumerate(self.rows[m:]):
			if end:
				break
			for j, box in enumerate(row[n:]):
				boxes.append(box)
				num += 1
				if num == n + 1:
					end = True
					break
		boxes = boxes[1:]
		return boxes

	def find_pos(self, box):
		cx, cy = box['cx'], box['cy']
		for b in self.boxes:
			if b['cx'] == cx and b['cy'] == cy:
				return b['pos']

	def find_next_downward(self, box):
		m, n = self.find_pos(box)
		if m >= len(self.rows):
			return None
		cands = self.rows[m + 1]
		cands = sorted(cands, key=lambda b: (b['cx'] - box['cx']) ** 2 + (b['cy'] - box['cy']) ** 2)
		return cands[0]

	def connect_vertical_downward(self, box):
		box['pos'] = self.find_pos(box)
		m, n = box['pos']
		boxset = []

		def is_vertically_adjacent(b1, b2):
			ro = 0.2  # 横向超出占行宽的最大比重
			rv = 3  # 纵向距离占行高的最大比重
			if b2['cx'] > b1['xmax'] or b2['cx'] < b1['xmin']: return False
			if b2['cy'] < b2['cy'] or (b2['cy'] - b1['cy']) > b1['h'] * rv: return False

			ofl = b1['xmin'] - b2['xmin'] if b2['xmin'] < b1['xmin'] else 0
			ofr = b2['xmax'] - b1['xmax'] if b2['xmax'] > b1['xmax'] else 0
			off = ofl + ofr
			if off > ro * b1['w']: return False
			return True

		for row in self.rows[m:]:
			for b in row[n:]:
				if len(boxset) == 0:
					boxset.append(b)
					continue
				if is_vertically_adjacent(boxset[-1], b): boxset.append(b)
		self.cache['boxset']=boxset
		return boxset

	def orgnize_boxes(self,boxes):
		rows = []
		boxes.sort(key=lambda box: int(box['cy']))
		for box in boxes:
			if len(rows) == 0:
				row = [box]
				rows.append(row)
				continue
			last_box = rows[-1][-1]
			if box['cy'] <= last_box['cy'] + int(last_box['h'] * 0.5):
				rows[-1].append(box)
			else:
				row = [box]
				rows.append(row)
		for row in rows:
			row.sort(key=lambda box: int(box['cx']))
		return rows

	def find_boxes(self, key, boxes=None):
		boxes = self.boxes if not boxes else boxes
		boxset = []
		[boxset.append(box) if key(box) else None for box in boxes]
		return boxset

	def in_area(self, box, xr=None, yr=None):
		assert self.imsize is not None
		h, w = self.imsize
		cx, cy = box['cx'], box['cy']
		if xr and not (cx >= xr[0] * w and cx <= xr[1] * w):
			return False
		if yr and not (cy >= yr[0] * h and cy <= yr[1] * h):
			return False
		return True

	def __find_box_by_str(self, boxes, pattern):
		import re
		boxes2 = []
		for box in boxes:
			res = re.findall(pattern, box['text'])
			if len(res) != 0:
				boxes2.append(box)
		return boxes2

	def find_box_by_str(self, boxes, patterns):
		for pattern in patterns:
			boxset = self.__find_box_by_str(boxes, pattern)
			if len(boxset):
				return boxset[0]

	def print_rows(self):
		for row in self.rows:
			print(row)