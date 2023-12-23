import re
from sys import argv

import cv2
import numpy as np

image = np.zeros((64, 128), dtype=np.uint8)
data = ''

try:
    while True:
        data += re.sub(r'\s', '', input())
except EOFError:
    pass

for i in range(0, len(data), 2):
    index = i // 2
    ch = int(data[i: i + 2], 16)

    for j in range(8):
        if ch & (1 << j):
            image[8 * (index // 128) + j, index % 128] = 255

image = cv2.resize(image, np.array(image.shape[::-1]) * 4, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(argv[1], image)
