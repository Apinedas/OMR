import numpy as np
import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def split_boxes(img, num_cols, num_rows):
    cols = np.array_split(img, num_cols, axis=1)
    boxes = []
    for c in cols:
        rows = np.array_split(c, num_rows, axis=0)
        for box in rows:
            boxes.append(box)
    return boxes


def rect_contour(contours):
    rect_con = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > 1000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if len(approx) == 4:
                rect_con.append(i)
    rect_con.reverse()
    return rect_con


def get_corner_points(cont):
    peri = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
    return approx


def reorder(actual_points):
    actual_points = actual_points.reshape((4, 2))
    new_points = np.zeros((4, 1, 2), np.int32)
    add = actual_points.sum(1)
    new_points[0] = actual_points[np.argmin(add)]
    new_points[3] = actual_points[np.argmax(add)]
    diff = np.diff(actual_points, axis=1)
    new_points[1] = actual_points[np.argmin(diff)]
    new_points[2] = actual_points[np.argmax(diff)]
    return new_points


def code_manipulation(img, code_points):
    fixed_points = np.float32([[0, 0], [500, 0], [0, 500], [500, 500]])
    custom_config = r'--oem 3 --psm 6'
    matrix = cv2.getPerspectiveTransform(code_points, fixed_points)
    img_warp_colored = cv2.warpPerspective(img, matrix, (500, 500))
    img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)
    img_warp_gray = img_warp_gray[200:480, :]
    print(pytesseract.image_to_string(img_warp_gray, config=custom_config))
