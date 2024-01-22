import cv2
import numpy as np
from typing import List, Tuple, Generator
from os import listdir
from tqdm import tqdm

def detect(
    img_path: str, 
    face_classifier: cv2.CascadeClassifier = None
) -> Tuple[Tuple[int], np.ndarray]:
    if face_classifier is None:
        face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    max_face_area = 0
    max_face = None
    for face in faces:
        sqare = face[2] * face[3] # w * h
        if sqare > max_face_area:
            max_face_area = sqare
            max_face = face

    x, y, w, h = max_face[0], max_face[1], max_face[2], max_face[3]
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 10)

    return max_face, img

def detect_mul(
    photo_paths: List[str]
) -> Generator[Tuple[Tuple[int], np.ndarray], None, None]:
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    for path in photo_paths:
        yield detect(path, face_classifier)
