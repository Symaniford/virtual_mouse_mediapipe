# Licensed under the Apache License, Version 2.0 (the "License"). 
# Use Google Mediapipe to make a hand-control virtual mouse
import time
from math import sqrt
from pickle import FALSE, TRUE

import cv2
import mediapipe as mp
from numpy import array, std
from pymouse import PyMouse
from win32api import GetSystemMetrics


def get_screen_size():
    wide = GetSystemMetrics(0)
    high = GetSystemMetrics(1)
    return wide, high


def distance(*ri):
    sum_d = 0
    for i in range(len(ri)):
        sum_d = sum_d + ri[i] * ri[i]
    dist = sqrt(sum_d)
    return dist


def screen_factor(screen_size_x, screen_size_y, imgWidth, imgHeight):
    screen_factor_x = screen_size_x / imgWidth
    screen_factor_y = screen_size_y / imgHeight
    return screen_factor_x, screen_factor_y


def corrected_move(xPoslist, yPoslist, xPos, yPos, fps, crop, result8_l):
    xPoslist.append(xPos)  # store them for some functions
    yPoslist.append(yPos)
    if len(xPoslist) > 10:  # control the length of list
        xPoslist.pop(0)
        xPos_now = xPoslist[-1]
        xPos_lastone = xPoslist[-2]

    if len(yPoslist) > 10:
        yPoslist.pop(0)
        yPos_now = yPoslist[-1]
        yPos_lastone = yPoslist[-2]

    d_x = xPos_now - xPos_lastone  # delta x,y
    d_y = yPos_now - yPos_lastone

    # prevent from cursor not moving when finger is in a snow move
    d_tx = xPoslist[-1] - xPoslist[-5]
    d_ty = yPoslist[-1] - yPoslist[-5]
    r_list = array([distance(xPoslist[-1], yPoslist[-1]),
                    distance(xPoslist[-2], yPoslist[-2]),
                    distance(xPoslist[-3], yPoslist[-3]),
                    distance(xPoslist[-4], yPoslist[-4]),
                    distance(xPoslist[-5], yPoslist[-5])])

    # standard minus of movement of continual 5 points
    r_std = std(r_list, ddof=1)
    d_r = sqrt(d_x * d_x + d_y * d_y)
    d_tr = sqrt(d_tx * d_tx + d_ty * d_ty)
    # highlight the finger
    cv2.circle(img, (xPos, yPos), 10, (0, 0, 180), -1)

#   decrease shake of the cursor
    if fps < 15:
        sensitivity1 = 3 + (fps - 15) * 0.05
        sensitivity2 = 2 + (fps - 15) * 0.1
    else:
        sensitivity1 = 3 + (fps - 15) * 0.035
        sensitivity2 = 2 + (fps - 15) * 0.07
    #   print(sensitivity1,sensitivity2)
    #   sensitivity depends on fps.
    result_x = int(1 / (1 - 2 * crop) * scr_pos_x - crop * screen_size_x)
    result_y = int(1 / (1 - 2 * crop) * scr_pos_y - crop * screen_size_y)
#    d_result_x = result_x - result8_l[0]
#    d_result_y = result_y - result8_l[1]
    if (abs(d_tr) > sensitivity1 * r_std or abs(d_r) > sensitivity2):
        #   judge: if distance of a movement is shorter than a jitter.
        #   if so, cancel the movement. and consider a snow but long movement,
        #   the latter ludge is to ensure the cursor follow the finger
        #   move the cursor according to the finger locating
        mouse.move(result_x, result_y)
    #    for i in range(1, 6):
    #        mouse.move(result_x + int(i / 5 * d_result_x),
    #                   result_y + int(i / 5 * d_result_y))

    return [result_x, result_y]


#   parameter for calculating FPS
pTime = 0
pTime1 = 0
cTime = 0
fps = 0
avg_fps = 0
switch_fps = 0
k = 0
l = 0

#   parameter for cursor locations
xPos = 0
yPos = 0
xPos_now = 0
yPos_now = 0
xPos_lastone = 0
yPos_lastone = 0
zPos_lastone = 0

xPoslist = []
yPoslist = []
z_list = []
z_last_list = []

loc_list = []
loc_last_list = []
loc_x = []
loc_y = []
loc_z = []
loc_lx = []
loc_ly = []
loc_lz = []
dloc_x = []
dloc_y = []
dloc_z = []

result8_l = [0, 0]
result8 = [0, 0]

for t in range(21):
    loc_list.append([0, 0, 0])
    loc_last_list.append([0, 0, 0])
    loc_x.append(0)
    loc_y.append(0)
    loc_z.append(0)
    loc_lx.append(0)
    loc_ly.append(0)
    loc_lz.append(0)
    dloc_x.append(0)
    dloc_y.append(0)
    dloc_z.append(0)

for i in range(12):
    xPoslist.append(0)
    yPoslist.append(0)


screen_size = get_screen_size()
screen_size_x = screen_size[0]
screen_size_y = screen_size[1]
print(screen_size)

#   parameter for image flip
if_flip = 0

#   get image from every available camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if FALSE:
    # camera on laptops often shows mirror image
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if_flip = 1
    print('image flip on')

#   hands recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)

#   mpDraw = mp.solutions.drawing_utils
#   parameter settings of model of hands: mp.solutions->__init__.py->hands.py AND FIND def __init__.

#   main part
while TRUE:
    ret, img = cap.read()
    imgWidth = img.shape[1]  # size of image
    imgHeight = img.shape[0]
    mouse = PyMouse()
    crop = 0.1
    zoom = screen_factor(screen_size_x, screen_size_y, imgWidth, imgHeight)
#   you can flip the image using codes below
    if if_flip == 1:
        img = cv2.flip(img, 1)

    if ret:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # color the image
        result = hands.process(imgRGB)
    #    use codes below to print multi hand landmarks
    #    print(result.multi_hand_landmarks)

        if result.multi_hand_landmarks:

            for handLms in result.multi_hand_landmarks:
                #    use codes below to show connections of points
                #    mpDraw.draw_landmarks(img, handLms,mpHands.HAND_CONNECTIONS)
                #sensitivity3 = round(1 + (15 - avg_fps) * 0.01, 3)
                n_z = 0
                sum_dx = 0
                sum_dy = 0
                sum_dz = 0
                for i, lm in enumerate(handLms.landmark):

                    loc_last_list[i] = loc_list[i]
                    loc_lx[i] = loc_last_list[i][0]
                    loc_ly[i] = loc_last_list[i][1]
                    loc_lz[i] = loc_last_list[i][2]

                    loc_list[i] = [lm.x, lm.y, lm.z]
                    loc_x[i] = loc_list[i][0]
                    loc_y[i] = loc_list[i][1]
                    loc_z[i] = loc_list[i][2]

                    dloc_x[i] = loc_x[i] - loc_lx[i]
                    dloc_y[i] = loc_y[i] - loc_ly[i]
                    dloc_z[i] = loc_z[i] - loc_lz[i]

                    if loc_z[i] - loc_lz[i] < 0:
                        n_z = n_z + 1

                ##    click_judge = 0

                # if i != 8:
                # if abs(dloc_x[i]) > 0.0005 * sensitivity3 and abs(dloc_y[i]) > 0.0005 * sensitivity3:
                ##            click_judge = click_judge + 1

                    if i == 8:  # 8 for index finger
                        xPos = int(lm.x * imgWidth)
                        yPos = int(lm.y * imgHeight)
                        # zoom from image to screen
                        scr_pos_x = int(xPos * zoom[0])
                        scr_pos_y = int(yPos * zoom[1])
                    #    mouse.move(scr_pos_x, scr_pos_y)
                        result8 = corrected_move(
                            xPoslist, yPoslist, xPos, yPos, fps, crop, result8_l)
                        result8_l = result8
            #    print(abs(distance(loc_x[8], loc_y[8]) -
            #          distance(loc_x[12], loc_y[12])), loc_z[8])
            #    list1.append(abs(distance(loc_x[8], loc_y[8]) - distance(loc_x[12], loc_y[12])))
            #    list2.append(loc_z[8])
            #    col1 = "X"
            #    col2 = "Y"
            #    data = pd.DataFrame({col1:list1,col2:list2})
            #    data.to_excel('sample_data1.xlsx', sheet_name='sheet1', index=False)
                dis_8_12 = abs(
                    distance(loc_x[8], loc_y[8]) - distance(loc_x[12], loc_y[12]))
                dis_l_8_12 = abs(
                    distance(loc_lx[8], loc_ly[8]) - distance(loc_lx[12], loc_ly[12]))
                if dis_8_12 < 0.02 and dis_l_8_12 > 0.02:
                    mouse.click(result8[0], result8[1], 1)
            # if n_z > 18 and sum_dz < - 0.06 * sensitivity3 and click_judge < 1 and abs(dloc_x[8]) < 0.005 * sensitivity3 and abs(dloc_y[8]) < 0.005 * sensitivity3:
                ##    mouse.click(result8[0], result8[1], 1)
                # print("click")

        cTime = time.time()  # calculate frame per second
        fps = 1 / (cTime - pTime1)
        pTime1 = cTime
        if switch_fps == 1 or k == 0:
            pTime = cTime
            switch_fps = 0

        if cTime - pTime > 1:
            avg_fps = k / (cTime - pTime)
            k = 0
            switch_fps = 1

        k = k + 1
        img = img[int(crop * imgHeight):int((1 - crop) * imgHeight),
                  int(crop * imgWidth):int((1 - crop) * imgWidth)]

        cv2.putText(img, f"Average FPS : {int(avg_fps)}, press esc for quit",
                    (20, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
        cv2.imshow('touchboard', img)

        if cv2.waitKey(1) == 27:  # esc for quit
            break
