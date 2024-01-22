import numpy as np
import cv2
from typing import List, Tuple
from tqdm import tqdm

from ._detection import detect_mul

def img_shift(img, x_shift, y_shift):
    x_pad = (0, -x_shift) if x_shift < 0 else (x_shift, 0)
    y_pad = (0, -y_shift) if y_shift < 0 else (y_shift, 0)

    img = np.pad(img, (y_pad, x_pad, (0, 0)))

    if x_shift != 0:
        if x_shift > 0: img = img[:, :-x_shift]
        else: img = img[:, -x_shift:]
    if y_shift != 0:
        if y_shift > 0: img = img[:-y_shift, :]
        else: img = img[-y_shift:, :]

    return img

def img_scale(img, factor, center):
    M = cv2.getRotationMatrix2D(center, 0, factor)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

def align(
    detected: List[Tuple[Tuple[int], np.ndarray]]
) -> List[np.ndarray]:
    def get_center_dot(x, y, w, h):
        return (x + w/2, y + h/2)

    # Calculating average face center and the smallest (furtherest) face 
    avg_dot = [0, 0]
    max_w = 0
    for (x, y, w, h), _ in detected:
        dot = get_center_dot(x, y, w, h)
        avg_dot[0] += dot[0]
        avg_dot[1] += dot[1]
        if w > max_w: max_w = w
    avg_dot = tuple([n / len(detected) for n in avg_dot])

    for i in tqdm(range(len(detected)), desc="Aligning photos"):
        # detected[i] - ((x, y, w, h), img)
        dot = get_center_dot(
            detected[i][0][0], detected[i][0][1],
            detected[i][0][2], detected[i][0][3],
        )
        img = detected[i][1]
        x_shift = int(round(avg_dot[0] - dot[0]))
        y_shift = int(round(avg_dot[1] - dot[1]))
        img = img_shift(img, x_shift, y_shift)
        img = img_scale(img, max_w / detected[i][0][2], avg_dot)
        detected[i] = img

    return detected
