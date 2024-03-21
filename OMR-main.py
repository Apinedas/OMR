import cv2
import numpy as np
import utlis
import os

folder = "Hojas de respuesta"
ans_sheets = os.listdir(folder)
for sheet in ans_sheets:
    ########################################################################
    pathImage = "{}/{}".format(folder, sheet)
    heightImg = 2000
    widthImg = 2000
    pickedAnswers_s1 = []
    pickedAnswers_s2 = []
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
    for img in init_array:
        cv2.imshow("Hola", cv2.resize(img, (700, 700)))
        cv2.waitKey(0)

    gotContours = []

    for i in range(0, len(rectContours)):
        gotContours.append(utlis.get_corner_points(rectContours[i]))
        gotContours[i] = utlis.reorder(gotContours[i])
        # cv2.drawContours(answerImage, gotContours[i], -1, (0, 255, 0), 40)
        # cv2.imshow("Contours", cv2.resize(answerImage, (500, 500)))
        # cv2.waitKey()

    fixed_points = np.float32([[0, 0], [widthImg, 0], [0, heightImg],  [widthImg, heightImg]])
    answers_points = np.float32(gotContours[0])

    matrix = cv2.getPerspectiveTransform(answers_points, fixed_points)
    imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.threshold(imgWarpGray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    # cv2.imshow("Thresh", cv2.resize(imgThresh, (500, 500)))
    # cv2.waitKey()
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
    
    print(selected_answers_index)

'''
    i = 0
    j = 0
    for box in boxes:
        if sesion == "Sesion 2" and "9.jpg" in sheet:
            cv2.imshow(subject[1], box)
            cv2.waitKey(0)
        totalPixels = cv2.countNonZero(box)
        answers[i][j] = totalPixels
        i += 1
        if i == num_rows:
            j += 1
            i = 0
    answers = np.transpose(answers)
    selected_answers_index = []
    for x in range(0, num_cols):
        arr = answers[x]
        if np.mean(arr) > 0 and np.max(arr) / np.mean(arr) >= 1.4:
            selected_index = np.where(arr == np.max(arr))
            selected_answers_index.append(selected_index[0][0])
        else:
            selected_answers_index.append(-1)
    if "Reading" in subject[1] and subject[1] != "Reading 4":
        del (selected_answers_index[10])
    if "Science" in subject[1] and sesion == "Sesion 1":
        for i in range(0, 29):
            if selected_answers_index[i] >= 0:
                selected_answers_index[i] += 1
    if "Science 2" == subject[1] and sesion == "Sesion 2":
        del selected_answers_index[4:]
    if sesion == "Sesion 2" and subject[1] == "English 4":
        del selected_answers_index[10:]
    session_answers[subject[1]] = selected_answers_index
if sesion == "Sesion 1":
    correct_answers = {"Math": [], "Socials": [], "Reading 1": [], "Reading 2": [], "Reading 3": [],
                        "Reading 4": [], "Science": []}
    total_correct_answers = {"Math": 0, "Socials": 0, "Reading 1": 0, "Reading 2": 0, "Reading 3": 0,
                                "Reading 4": 0, "Biology": 0, "Chemistry": 0, "Physiscs": 0, "CTS": 0}
else:
    correct_answers = {"Socials": [], "Math": [], "Science 1": [], "Science 2": [], "English 1": [],
                        "English 2": [], "English 3": [], "English 4": []}
    total_correct_answers = {"Socials": 0, "Math": 0, "Biology": 0, "Chemistry": 0, "Physiscs": 0, "CTS": 0,
                                "English 1": 0, "English 2": 0, "English 3": 0, "English 4": 0}
for subject, questions in session_answers.items():
    for i in range(0, len(questions)):
        if questions[i] == right_answers[sesion][subject][i]:
            correct_answers[subject].append(1)
            if "Science" in subject and sesion == "Sesion 1" and i in range(0, 11):
                total_correct_answers["Biology"] += 1
            elif "Science" in subject and sesion == "Sesion 1" and i in range(11, 16):
                total_correct_answers["Physiscs"] += 1
            elif "Science" in subject and sesion == "Sesion 1" and i in range(16, 28):
                total_correct_answers["Chemistry"] += 1
            elif "Science" in subject and sesion == "Sesion 1" and i == 28:
                total_correct_answers["CTS"] += 1
            elif "Science 1" == subject and sesion == "Sesion 2" and i in range(0, 9):
                total_correct_answers["Biology"] += 1
            elif ("Science 1" == subject and i in [9, 10, 12]) or ("Science 2" == subject and i in [1, 2]):
                total_correct_answers["Physiscs"] += 1
            elif ("Science 1" == subject and (i in [11, 24] or i in range(13, 20))) or ("Science 2" == subject
                                                                                        and i == 0):
                total_correct_answers["Chemistry"] += 1
            elif ("Science 1" == subject and (i in range(20, 24))) or ("Science 2" == subject and i == 3):
                total_correct_answers["CTS"] += 1
            else:
                total_correct_answers[subject] += 1
        elif subject == "Math" and sesion == "Sesion 1" and i == 5 and questions[i] == 1:
            correct_answers[subject].append(1)
            total_correct_answers[subject] += 1
        else:
            correct_answers[subject].append(0)
if sesion == "Sesion 1":
    results_sheet["B{}".format(actual_row)] = sheet
    results_sheet["C{}".format(actual_row)] = total_correct_answers["Math"]
    results_sheet["D{}".format(actual_row)] = total_correct_answers["Reading 1"] + \
                                                total_correct_answers["Reading 2"] + \
                                                total_correct_answers["Reading 3"] + \
                                                total_correct_answers["Reading 4"]
    results_sheet["E{}".format(actual_row)] = total_correct_answers["Socials"]
    results_sheet["F{}".format(actual_row)] = total_correct_answers["Biology"]
    results_sheet["G{}".format(actual_row)] = total_correct_answers["Chemistry"]
    results_sheet["H{}".format(actual_row)] = total_correct_answers["Physiscs"]
    results_sheet["I{}".format(actual_row)] = total_correct_answers["CTS"]
    actual_row += 1
else:
    results_sheet["B{}".format(actual_row)] = sheet
    results_sheet["J{}".format(actual_row)] = total_correct_answers["Socials"]
    results_sheet["K{}".format(actual_row)] = total_correct_answers["Math"]
    results_sheet["L{}".format(actual_row)] = total_correct_answers["Biology"]
    results_sheet["M{}".format(actual_row)] = total_correct_answers["Chemistry"]
    results_sheet["N{}".format(actual_row)] = total_correct_answers["Physiscs"]
    results_sheet["O{}".format(actual_row)] = total_correct_answers["CTS"]
    results_sheet["P{}".format(actual_row)] = total_correct_answers["English 1"] + \
                                                total_correct_answers["English 2"] + \
                                                total_correct_answers["English 3"] + \
                                                total_correct_answers["English 4"]
    actual_row += 1
'''
