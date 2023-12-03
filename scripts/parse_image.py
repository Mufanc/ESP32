from os import path
from sys import argv

import cv2
import numpy as np


def dither_grayscale(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary_img = img.copy()

    # Apply Floyd-Steinberg dithering algorithm
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            old_pixel = img[y, x]
            new_pixel = 0 if old_pixel < 128 else 255
            binary_img[y, x] = new_pixel

            quant_error = old_pixel - new_pixel

            if x < img.shape[1] - 1:
                img[y, x + 1] = img[y, x + 1] + quant_error * 7 / 16

            if x > 0 and y < img.shape[0] - 1:
                img[y + 1, x - 1] = img[y + 1, x - 1] + quant_error * 3 / 16

            if y < img.shape[0] - 1:
                img[y + 1, x] = img[y + 1, x] + quant_error * 5 / 16

            if x < img.shape[1] - 1 and y < img.shape[0] - 1:
                img[y + 1, x + 1] = img[y + 1, x + 1] + quant_error * 1 / 16

    display_size = (np.array(binary_img.shape) * 1)[::-1]
    display_img = cv2.resize(binary_img, display_size, interpolation=cv2.INTER_NEAREST)
    cv2.imshow('image-parser', display_img)
    cv2.waitKey(5000)

    binary_img[binary_img == 255] = 1
    binary_img = np.packbits(binary_img.reshape((img.shape[0] * img.shape[1], )))

    print(f'compressed size: {len(binary_img)} bytes')

    with open(argv[2], 'wb') as fp:
        fp.write(bytes(binary_img))


if __name__ == '__main__':
    if len(argv) < 3:
        print(f'Usage: python {path.basename(__file__)} <input> <output>')
        exit()

    image = cv2.imread(argv[1])

    # Call the function with the image path
    dither_grayscale(image)
