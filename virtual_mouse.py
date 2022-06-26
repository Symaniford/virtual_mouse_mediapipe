import sys
import time
from math import sqrt
from pickle import FALSE, TRUE

import cv2
import mediapipe as mp
from numpy import array, std
from pymouse import PyMouse
#   from PyQt5 import QtChart
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPixmap
#   from PyQt5.QtChart import QValueAxis, QScatterSeries
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow
from win32api import GetSystemMetrics
from win32 import win32api, win32gui, win32print
from win32.lib import win32con
#   from PyQt5.QtCore import Qt
#   import sys

def get_real_resolution():
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return wide, high

#   def get_screen_size():
#       wide = GetSystemMetrics(0)
#       high = GetSystemMetrics(1)
#       return wide, high


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


def corrected_move(xPoslist, yPoslist, xPos, yPos, fps, crop, sensitivity):
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
#    print(result_x,result_y)
#    d_result_x = result_x - result8_l[0]
#    d_result_y = result_y - result8_l[1]
    if (abs(d_tr) > sensitivity1 * sensitivity * r_std or abs(d_r) > sensitivity2 * sensitivity):
        #   judge: if distance of a movement is shorter than a jitter.
        #   if so, cancel the movement. and consider a snow but long movement,
        #   the latter ludge is to ensure the cursor follow the finger
        #   move the cursor according to the finger locating
        mouse.move(result_x, result_y)
    #    for i in range(1, 6):
    #        mouse.move(result_x + int(i / 5 * d_result_x),
    #                   result_y + int(i / 5 * d_result_y))

    return [result_x, result_y]


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(850, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView(MainWindow)
        self.graphicsView.setGeometry(QtCore.QRect(20, 20, 620, 470))
        self.graphicsView.setObjectName("graphicsView")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(650, 320, 161, 41))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    #    self.buttonBox.setStandardButtons(
    #        QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(650, 20, 141, 71))
        self.lcdNumber.setObjectName("lcdNumber")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(650, 120, 171, 41))
        self.checkBox.setObjectName("checkBox")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(20, 520, 121, 31))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
    #    self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
    #    self.checkBox_2.setGeometry(QtCore.QRect(650, 230, 171, 51))
    #    self.checkBox_2.setObjectName("checkBox_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(190, 520, 121, 31))
        self.label.setObjectName("label")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(650, 185, 181, 31))
        self.checkBox_3.setObjectName("checkBox_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.checkBox.setText(_translate("MainWindow", "image flip"))
    #    self.checkBox_2.setText(_translate("MainWindow", "locus"))
        self.label.setText(_translate("MainWindow", "sensitivity"))
        self.checkBox_3.setText(_translate("MainWindow", "click mode"))

    def image_flip_button(self):
        if self.checkBox.isChecked():
            return 1
        else:
            return 0

    def click_mode_button(self):
        if self.checkBox_3.isChecked():
            return 1
        else:
            return 0


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


screen_size = get_real_resolution()
screen_size_x = screen_size[0]
screen_size_y = screen_size[1]

#   parameter for image flip
if_flip = 0

#   get image from every available camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cap == FALSE:
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if cap == FALSE:
        cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

#   hands recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)

app = QApplication(sys.argv)
mainWindow = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mainWindow)
mainWindow.setWindowTitle("Virtual Mouse")
mainWindow.setWindowIcon(QIcon('C:/Users/YMZOWL/Desktop/vrmouse/hand.ico'))
ui.lcdNumber.setDigitCount(4)
ui.horizontalSlider.setMinimum(20)
ui.horizontalSlider.setMaximum(100)
mainWindow.show()


#   mpDraw = mp.solutions.drawing_utils
#   parameter settings of model of hands: mp.solutions->__init__.py->hands.py AND FIND def __init__.
#   main part
while TRUE:
    ret, img = cap.read()
    imgWidth1 = img.shape[1]  # size of image
    imgHeight1 = img.shape[0]
    img = img[int((imgHeight1 - 480) / 2) : int((imgHeight1 + 480) / 2), int((imgWidth1 - 640) / 2) : int((imgWidth1 + 640) / 2)]
    crop = 0.1
    imgWidth = img.shape[1]
    imgHeight = img.shape[0]
    #   img = img[int(crop * imgHeight):int((1 - crop) * imgHeight),int(crop * imgWidth):int((1 - crop) * imgWidth)]
    img_c = img
    mouse = PyMouse()
    if_flip = ui.image_flip_button()
    if_click = ui.click_mode_button()
    zoom = screen_factor(screen_size_x, screen_size_y, imgWidth, imgHeight)
#   you can flip the image using codes below
    if if_flip == 1:
        img = cv2.flip(img, 1)
        img_c = cv2.flip(img_c, 1)

    if ret:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # color the image
        imgRGB_c = cv2.cvtColor(img_c, cv2.COLOR_BGR2RGB)
        result = hands.process(imgRGB)

    #    use codes below to print multi hand landmarks
    #    print(result.multi_hand_landmarks)
        ui.lcdNumber.display(avg_fps)
        sensitivity = ui.horizontalSlider.value() / 100
        if result.multi_hand_landmarks:

            for handLms in result.multi_hand_landmarks:
                #    use codes below to show connections of points
                #    mpDraw.draw_landmarks(img, handLms,mpHands.HAND_CONNECTIONS)
                #sensitivity3 = round(1 + (15 - avg_fps) * 0.01, 3)
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

                    if i == 8:  # 8 for index finger
                        xPos_8 = int(lm.x * imgWidth)
                        yPos_8 = int(lm.y * imgHeight)
                        # zoom from image to screen
                        scr_pos_x = int(xPos_8 * zoom[0])
                        scr_pos_y = int(yPos_8 * zoom[1])
                    #    print(scr_pos_x,scr_pos_y)
                        cv2.circle(imgRGB_c, (xPos_8, yPos_8), 10, (0, 0, 180), -1)
                        cv2.circle(imgRGB_c, (xPos_8, yPos_8),
                                   10, (0, 0, 180), -1)
                        result8 = corrected_move(
                            xPoslist, yPoslist, xPos_8, yPos_8, fps, crop, sensitivity)
                    #    print(result8)
                        result8_l = result8
                    if i == 12:
                        xPos_12 = int(lm.x * imgWidth)
                        yPos_12 = int(lm.y * imgHeight)

                dis_8_12 = abs(
                    distance(loc_x[8], loc_y[8]) - distance(loc_x[12], loc_y[12]))
                dis_l_8_12 = abs(
                    distance(loc_lx[8], loc_ly[8]) - distance(loc_lx[12], loc_ly[12]))
                dis_4_5 = abs(
                    distance(loc_x[4], loc_y[4]) - distance(loc_x[5], loc_y[5]))
                dis_l_4_5 = abs(
                    distance(loc_lx[4], loc_ly[4]) - distance(loc_lx[5], loc_ly[5]))
                if dis_8_12 < 0.06 and if_click == 1:
                #    imgRGB_c = cv2.circle(
                #        imgRGB, (xPos_12, yPos_12), 10, (0, 0, 180), -1)
                    if dis_8_12 < 0.03 and dis_l_8_12 > 0.03:
                        mouse.click(result8_l[0], result8_l[1], 1)
                if dis_4_5 < 0.015 and dis_l_4_5 > 0.015 and if_click == 1:
                    mouse.click(result8_l[0], result8_l[1], 2)
            # if n_z > 18 and sum_dz < - 0.06 * sensitivity3 and click_judge < 1 and abs(dloc_x[8]) < 0.005 * sensitivity3 and abs(dloc_y[8]) < 0.005 * sensitivity3:
                ##    mouse.click(result8[0], result8[1], 1)
                # print("click")
        ph = QImage(imgRGB_c, imgWidth, imgHeight, QImage.Format_RGB888)
        ph1 = QPixmap.fromImage(ph)
        item1 = QtWidgets.QGraphicsPixmapItem(ph1)
        scene = QGraphicsScene()
        scene.addItem(item1)
        ui.graphicsView.setScene(scene)

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
    #    img = img[int(crop * imgHeight):int((1 - crop) * imgHeight),
    #              int(crop * imgWidth):int((1 - crop) * imgWidth)]

    #    cv2.putText(img, f"Average FPS : {int(avg_fps)}, press esc for quit",
    #                (20, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
    #    cv2.imshow('touchboard', img)

        if cv2.waitKey(1) == 27:  # esc for quit
            break
