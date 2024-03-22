import cv2
import numpy as np
import utlis
import os
import pandas as pd

folder = "Hojas de respuesta"
ans_sheets = os.listdir(folder)
correct_answers = [1, 2, 4, 3, 2, 1, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0]
all_corrections = {"Name": []}
for i in range(0, len(correct_answers)):
    all_corrections[f"{i + 1}"] = []

for sheet in ans_sheets:
    ########################################################################
    pathImage = "{}/{}".format(folder, sheet)
    heightImg = 2000
    widthImg = 2000
    pickedAnswers_s1 = []
    pickedAnswers_s2 = []
    all_corrections["Name"].append(sheet[:-4])
    ########################################################################

    img = cv2.imread(pathImage)
    img = cv2.resize(img, (widthImg, heightImg))
    imgContours = img.copy()
    imgDataContour = img.copy()
    answerImage = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 3)
    imgCanny = cv2.Canny(imgBlur, 10, 70, None, 3, True)
    imgBlank = np.zeros_like(img)
    init_array = [img, imgGray, imgBlur, imgCanny, imgContours]
    contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rectContours = utlis.rect_contour(contours)
    cv2.drawContours(imgContours, rectContours, -1, (0, 255, 0), 10)
    # for img in init_array:
    #     # cv2.imshow("Hola", cv2.resize(img, (700, 700)))
    #     # cv2.waitKey(0)

    gotContours = []

    for i in range(0, len(rectContours)):
        gotContours.append(utlis.get_corner_points(rectContours[i]))
        gotContours[i] = utlis.reorder(gotContours[i])

    fixed_points = np.float32([[0, 0], [widthImg, 0], [0, heightImg],  [widthImg, heightImg]])
    try:
        answers_points = np.float32(gotContours[0])
    except IndexError:
        answers_points = np.array([[[172, 562]], [[1774, 560]], [[168, 1854]], [[1770, 1852]]], dtype=np.float32)
    
    matrix = cv2.getPerspectiveTransform(answers_points, fixed_points)
    imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.threshold(imgWarpGray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    num_cols = 5
    num_rows = 31
    boxes = utlis.split_boxes(imgThresh, num_cols, num_rows)
    answers = np.zeros((num_rows, num_cols))
    j = k = 0
    for box in boxes:
        box = box[0:, 75:260]
        if j > 0 and k > 0:
            # cv2.imshow("Box", box)
            # cv2.waitKey(0)
            totalPixels = cv2.countNonZero(box)
            answers[j][k] = totalPixels
        j += 1
        if j == num_rows:
            k += 1
            j = 0

    selected_answers_index = []
    for x in range(1, num_rows):
        arr = answers[x]
        # print(f"Row: {x}, Answers: {arr}")
        if np.mean(arr) > 0 and np.max(arr) / np.mean(arr) >= 1.5:
            selected_index = np.where(arr == np.max(arr))
            selected_answers_index.append(selected_index[0][0])
        else:
            selected_answers_index.append(-1)
    
    for i in range(0, len(selected_answers_index)):
        if selected_answers_index[i] == correct_answers[i]:
            all_corrections[f"{i + 1}"].append("✅")
        elif correct_answers[i] == 0:
            all_corrections[f"{i + 1}"].append("Open")
        elif selected_answers_index[i] == -1:
            all_corrections[f"{i + 1}"].append("❓")
        else:
            all_corrections[f"{i + 1}"].append("❌")

df = pd.DataFrame(all_corrections)
df.to_excel('dict1.xlsx')
