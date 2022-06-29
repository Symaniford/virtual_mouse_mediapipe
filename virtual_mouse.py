import sys
import time
from math import sqrt
from pickle import FALSE, TRUE
#   import pyscreenshot as pyshot
import cv2
import mediapipe as mp
from numpy import array, std
from pymouse import PyMouse
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QWidget
from win32 import win32api, win32gui, win32print
from win32.lib import win32con
from win32api import GetSystemMetrics

#   get real resolution


def get_real_resolution() -> int:
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return wide, high

#   def get_screen_size():
#       wide = GetSystemMetrics(0)
#       high = GetSystemMetrics(1)
#       return wide, high


def distance(*ri) -> float:
    sum_d = 0
    for i in range(len(ri)):
        sum_d = sum_d + ri[i] * ri[i]
    dist = sqrt(sum_d)
    return dist


def theta_2f(f1: tuple, f2: tuple) -> float:
    dianji = (f1[0] * f2[0] + f1[1] * f2[1])
    length1 = sqrt(f1[0]*f1[0]+f1[1]*f1[1])
    length2 = sqrt(f2[0]*f2[0]+f2[1]*f2[1])
    theta = dianji / (length1 * length2)
    return theta
#   mapping from image to screen


def screen_factor(screen_size_x, screen_size_y, imgWidth, imgHeight) -> list:
    screen_factor_x = screen_size_x / imgWidth
    screen_factor_y = screen_size_y / imgHeight
    return screen_factor_x, screen_factor_y

##   control cursor by finger moving
#def screenshot_vr(x_8Pos,y_8Pos,x_12Pos,y_12Pos,x1Pos:list, y1Pos:list, x2Pos:list, y2Pos:list):
#    d_ad_y1 = []
#    d_ad_x1 = []
#    d_ad_x2 = []
#    d_ad_y2 = []
#    list_finish = 0
#    list_whole = [d_ad_x1,d_ad_x2,d_ad_y1,d_ad_y2,x1Pos,x2Pos,y1Pos,y2Pos]
#    if list_finish == 0:
#        for n in range(10):
#            for i in range(8):
#                list_whole[i].append(0)
#            if n == 9:
#                list_finish = 1
#    x1Pos.append(x_8Pos)
#    y1Pos.append(y_8Pos)
#    x2Pos.append(x_12Pos)
#    y2Pos.append(y_12Pos)
#    for i in range(8):
#        if len(list_whole[i]) > 10:
#            list_whole[i].pop(0)
#    for i in range(8):
#        if_shot = 0
#        d_ad_y1[i] = y1Pos[i+1] - y1Pos[i]
#        d_ad_y2[i] = y2Pos[i+1] - y2Pos[i]
#        if d_ad_y1[i] < 0 and d_ad_y2[i] < 0:
#            if_shot = 1
#        d_ad_x1[i] = x1Pos[i+1] - x1Pos[i]
#        d_ad_x2[i] = x2Pos[i+1] - x2Pos[i]
#        print(d_ad_x1,d_ad_x2,d_ad_y1,d_ad_y2)
#        if abs(d_ad_x1[i]) < 0.3 and abs(d_ad_x2[i]) < 0.3:
#            if_shot = 1
#    if sum(d_ad_y1) > 5 and sum(d_ad_x1) < 1 and if_shot == 1:
#        image_shot = pyshot.grab()
#        image_shot.show()
#        image_shot.save("screenshot_vrmouse.jpg")
        
    

def corrected_move(xPoslist: list, yPoslist: list, xPos: int, yPos: int, fps: float, crop: float, sensitivity: float) -> list:
    xPoslist.append(xPos)   
    yPoslist.append(yPos)
    if len(xPoslist) > 10:
        xPoslist.pop(0)
        xPos_now = xPoslist[-1]
        xPos_lastone = xPoslist[-2]

    if len(yPoslist) > 10:
        yPoslist.pop(0)
        yPos_now = yPoslist[-1]
        yPos_lastone = yPoslist[-2]

    d_x = xPos_now - xPos_lastone  # delta x,y
    d_y = yPos_now - yPos_lastone

#   prevent from cursor not moving when finger is in a snow move
    d_tx = xPoslist[-1] - xPoslist[-5]
    d_ty = yPoslist[-1] - yPoslist[-5]
    r_list = array([distance(xPoslist[-1], yPoslist[-1]),
                    distance(xPoslist[-2], yPoslist[-2]),
                    distance(xPoslist[-3], yPoslist[-3]),
                    distance(xPoslist[-4], yPoslist[-4]),
                    distance(xPoslist[-5], yPoslist[-5])])

#   standard minus of movement of continual points
    r_std = std(r_list, ddof=1)
    d_r = sqrt(d_x * d_x + d_y * d_y)
    d_tr = sqrt(d_tx * d_tx + d_ty * d_ty)

#   decrease shake of the cursor. sensitivity depends on fps.
    if fps < 15:
        sensitivity1 = 3 + (fps - 15) * 0.05
        sensitivity2 = 2 + (fps - 15) * 0.1
    else:
        sensitivity1 = 3 + (fps - 15) * 0.035
        sensitivity2 = 2 + (fps - 15) * 0.07

    result_x = int(1 / (1 - 2 * crop) * scr_pos_x - crop * screen_size_x)
    result_y = int(1 / (1 - 2 * crop) * scr_pos_y - crop * screen_size_y)
    if (abs(d_tr) > sensitivity1 * sensitivity * r_std or abs(d_r) > sensitivity2 * sensitivity):
        #   judge: if distance of a movement is shorter than a jitter.
        #   if so, cancel the movement. and consider a snow but long movement,
        #   the latter ludge is to ensure the cursor follow the finger
        #   move the cursor according to the finger locating
        mouse.move(result_x, result_y)

    return [result_x, result_y]

#   codes for pyqt mainwindow


class Ui_MainWindow(object):

    def setupUi(self, MainWindow) -> None:
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(870, 620)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView(MainWindow)
        self.graphicsView.setGeometry(QtCore.QRect(20, 20, 660, 500))
        self.graphicsView.setObjectName("graphicsView")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(700, 320, 160, 40))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setObjectName("buttonBox")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(700, 20, 140, 70))
        self.lcdNumber.setObjectName("lcdNumber")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(700, 180, 160, 30))
        self.checkBox.setObjectName("checkBox")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(20, 550, 120, 30))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(700, 120, 160, 30))
        self.checkBox_2.setObjectName("checkBox_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(190, 550, 121, 31))
        self.label.setObjectName("label")
        self.logo_mp = QtWidgets.QLabel(self.centralwidget)
        self.logo_mp.setGeometry(QtCore.QRect(700, 500, 150, 75))
        self.logo_mp.setObjectName("logo_mp")
    #    self.image_path = QtWidgets.QLineEdit(self.centralwidget)
    #    self.image_path.setGeometry(QtCore.QRect(360, 550, 120, 30))
    #    self.image_path.setObjectName("image_path")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(700, 300, 160, 30))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setGeometry(QtCore.QRect(700, 240, 160, 30))
        self.checkBox_4.setObjectName("checkBox_4")
        self.behavior_label = QtWidgets.QLabel(self.centralwidget)
        self.behavior_label.setGeometry(QtCore.QRect(360, 550, 120, 30))
        self.behavior_label.setObjectName("behavior_label")
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setGeometry(QtCore.QRect(700, 360, 160, 30))
        self.checkBox_5.setObjectName("checkBox_5")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow) -> None:
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.checkBox.setText(_translate("MainWindow", "IMAGE FLIP"))
        self.checkBox_2.setText(_translate("MainWindow", "SHOW IMAGE"))
        self.label.setText(_translate("MainWindow", "STABILITY"))
        self.logo_mp.setText(_translate("MainWindow", "LOGO_MP"))
        self.behavior_label.setText(_translate("MainWindow", " "))
    #    self.image_path.setText(_translate("MainWindow", "IMAGE PATH"))
        self.checkBox_3.setText(_translate("MainWindow", "CLICK MODE"))
        self.checkBox_4.setText(_translate("MainWindow", "CURSOR MOVE"))
        self.checkBox_5.setText(_translate("MainWindow", "CAMERA SWITCH"))

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

    def show_image_button(self):
        if self.checkBox_2.isChecked():
            return 1
        else:
            return 0

    def cursor_move_button(self):
        if self.checkBox_4.isChecked():
            return 1
        else:
            return 0

    def camera_switch_button(self):
        if self.checkBox_5.isChecked():
            return 1
        else:
            return 0


#   parameter for calculating FPS
pTime, pTime1, cTime, fps, avg_fps, switch_fps, k, l = 0, 0, 0, 0, 0, 0, 0, 0
l_time_last, l_time_now, r_time_last, r_time_now = 0, 0, 0, 0
#   parameter for cursor locations
xPos,yPos,xPos_now,yPos_now = 0,0,0,0
xPos_lastone,yPos_lastone,zPos_lastone = 0,0,0

xPoslist = []
yPoslist = []
#   x1Pos = []
#   y1Pos = []
#   x2Pos = []
#   y2Pos = []

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
drag = 0

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
    


#   get screen size
screen_size = get_real_resolution()
screen_size_x = screen_size[0]
screen_size_y = screen_size[1]


#   get image from every available camera
try:
    cap_in = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ret_test, img_test = cap_in.read()
    imgWidth_test = img_test.shape[1]
    cap_in_available = TRUE

except:
    cap_in_available = FALSE
    pass

try:
    cap_ex = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    ret_test_1, img_test_1 = cap_ex.read()
    imgWidth_test_1 = img_test_1.shape[1]
    cap_ex_available = TRUE

except:
    cap_ex_available = FALSE
    pass

#   hands recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)

#   codes runing the mainwindow and initalization
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.setWindowTitle("Virtual Mouse")
    root = QtCore.QFileInfo(__file__).absolutePath()
    mainWindow.setWindowIcon(QIcon(root + '/logo_hand.ico'))
    ui.lcdNumber.setDigitCount(4)
    ui.horizontalSlider.setMinimum(20)
    ui.horizontalSlider.setMaximum(100)
    logo_vrmouse = QPixmap(root + '/logo_hand.png')
    logo_of_mediapipe = QPixmap(
        root + '/logo_mediapipe.png').scaled(ui.logo_mp.width(), ui.logo_mp.height())
    ui.logo_mp.setPixmap(logo_of_mediapipe)
    mainWindow.show()
    ui.behavior_label.setText("WAITING...")


#   mpDraw = mp.solutions.drawing_utils
#   parameter settings of model of hands: mp.solutions->__init__.py->hands.py AND FIND def __init__.

#   main part
while TRUE:
#    back_image_path = ui.image_path.text()
    camera_switch = ui.camera_switch_button()
    
    if cap_ex_available == FALSE:
        ui.checkBox_5.setDisabled(True)
    if camera_switch == 0:
        ret, img = cap_in.read()
    else:
        ret, img = cap_ex.read()
    imgWidth1 = img.shape[1]
    imgHeight1 = img.shape[0]
    crop = 0.1
    imgWidth = img.shape[1]
    imgHeight = img.shape[0]
    img_c = img
#   img_c is used in mainwindow.graphicsview
    mouse = PyMouse()
    if_flip = ui.image_flip_button()
    if_click = ui.click_mode_button()
    if_show_image = ui.show_image_button()
    if_cursor_move = ui.cursor_move_button()
    if if_cursor_move == 0 or if_click == 0:
        ui.behavior_label.setText("WAITING...")
    if if_show_image == 1:
        ui.checkBox.setDisabled(False)
    else:
        ui.checkBox.setDisabled(True)
    if if_cursor_move == 1:
        ui.checkBox_3.setDisabled(False)
    else:
        ui.checkBox_3.setDisabled(True)
        if_click = 0
    zoom = screen_factor(screen_size_x, screen_size_y, imgWidth, imgHeight)

#   image flip
    if if_flip == 1:
        img = cv2.flip(img, 1)
        img_c = cv2.flip(img_c, 1)
#  color the image and initialize
    if ret:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # color the image
        imgRGB_c = cv2.cvtColor(img_c, cv2.COLOR_BGR2RGB)
        result = hands.process(imgRGB)
        ui.lcdNumber.display(avg_fps)
        sensitivity = ui.horizontalSlider.value() / 100
        if result.multi_hand_landmarks:

            for handLms in result.multi_hand_landmarks:

                #   use codes below to show connections of points
                #               mpDraw.draw_landmarks(img, handLms,mpHands.HAND_CONNECTIONS)
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
                    

                    if i == 1:
                        xPos_1 = int(lm.x * imgWidth)
                        yPos_1 = int(lm.y * imgHeight)
                    if i == 5:
                        xPos_5 = int(lm.x * imgWidth)
                        yPos_5 = int(lm.y * imgHeight)
                    if i == 4:
                        xPos_4 = int(lm.x * imgWidth)
                        yPos_4 = int(lm.y * imgHeight)
                    if i == 8:  # 8 for index finger
                        xPos_8 = int(lm.x * imgWidth)
                        yPos_8 = int(lm.y * imgHeight)
                        # zoom from image to screen
                        scr_pos_x = int(xPos_8 * zoom[0])
                        scr_pos_y = int(yPos_8 * zoom[1])
                        cv2.circle(imgRGB_c, (xPos_8, yPos_8),
                                   10, (0, 0, 180), -1)
                        cv2.circle(imgRGB_c, (xPos_8, yPos_8),
                                   10, (0, 0, 180), -1)
                        if if_cursor_move == 1:

                            result8 = corrected_move(
                                xPoslist, yPoslist, xPos_8, yPos_8, fps, crop, sensitivity)

                        result8_l = result8
                    if i == 12:
                        xPos_12 = int(lm.x * imgWidth)
                        yPos_12 = int(lm.y * imgHeight)
                    if i == 20:
                        xPos_20 = int(lm.x * imgWidth)
                        yPos_20 = int(lm.y * imgHeight)

                dis_8_12 = abs(
                    distance(loc_x[8], loc_y[8]) - distance(loc_x[12], loc_y[12]))
                dis_l_8_12 = abs(
                    distance(loc_lx[8], loc_ly[8]) - distance(loc_lx[12], loc_ly[12]))
                dis_4_5 = abs(
                    distance(loc_x[4], loc_y[4]) - distance(loc_x[5], loc_y[5]))
                dis_l_4_5 = abs(
                    distance(loc_lx[4], loc_ly[4]) - distance(loc_lx[5], loc_ly[5]))
                dis_8_20 = abs(
                    distance(loc_x[8], loc_y[8]) - distance(loc_x[20], loc_y[20]))
                dis_l_8_20 = abs(
                    distance(loc_lx[8], loc_ly[8]) - distance(loc_lx[20], loc_ly[20]))
                theta_t_i_f = theta_2f(
                    (xPos_4 - xPos_1, yPos_4 - yPos_1), (xPos_8 - xPos_5, yPos_8 - yPos_5))
                if if_click == 1:
                    if dis_8_12 < 0.06:
                        cv2.circle(imgRGB_c, (xPos_12, yPos_12),
                                   10, (0, 0, 180), -1)
                        if dis_8_12 < 0.06 and dis_l_8_12 > 0.06:
                            l_time_now = time.time()
                            if l_time_now - l_time_last > 0.2:
                                mouse.click(result8_l[0], result8_l[1], 1)
                                ui.behavior_label.setText("LEFT CLICK")
                            l_time_last = l_time_now
                    if dis_8_20 < 0.2 and dis_l_8_20 > 0.2:
                        cv2.circle(imgRGB_c, (xPos_20, yPos_20),
                                   10, (0, 0, 180), -1)
                        r_time_now = time.time()
                        if l_time_now - r_time_last > 0.2:
                            mouse.click(result8_l[0], result8_l[1], 2)
                            ui.behavior_label.setText("RIGHT CLICK")

                            r_time_last = r_time_now
                    cursor = mouse.position()
                #    screenshot_vr(xPos_8,yPos_8,xPos_12,yPos_12,x1Pos,y1Pos,x2Pos,y2Pos)
                    if theta_t_i_f < 0.4 and if_cursor_move == 1:
                        if drag == 0:
                            win32api.mouse_event(
                                win32con.MOUSEEVENTF_LEFTDOWN, cursor[0], cursor[1], 0, 0)
                            drag = 1
                        mouse.move(result8[0], result8[1])
                    if drag == 1:
                        ui.behavior_label.setText("DRAGGING")
                    if theta_t_i_f > 0.4 and if_cursor_move == 1:
                        if drag == 1:
                            win32api.mouse_event(
                                win32con.MOUSEEVENTF_LEFTUP, cursor[0], cursor[1], 0, 0)
                            ui.behavior_label.setText(" ")
                            drag = 0


#   load image to graphicsview
        image_qtimage = QImage(
            imgRGB_c, imgWidth, imgHeight, QImage.Format_RGB888)
        image_qtview = QPixmap.fromImage(image_qtimage).scaled(
            ui.graphicsView.width(), ui.graphicsView.height())
        scene = QGraphicsScene()
        scene_none = QGraphicsScene()
        if if_show_image == 1:
            item_image = QtWidgets.QGraphicsPixmapItem(image_qtview)
            scene.addItem(item_image)
            ui.graphicsView.setScene(scene)
        if if_show_image == 0:
        #    if ui.image_path.text():
        #        logo_self_define = QPixmap(root + '/' + back_image_path).scaled(ui.graphicsView.width(), ui.graphicsView.height())
        #        item_none = QtWidgets.QGraphicsPixmapItem(logo_self_define)
        #    else:
            item_none = QtWidgets.QGraphicsPixmapItem(logo_vrmouse)
            scene_none.addItem(item_none)
            ui.graphicsView.setScene(scene_none)

#   calculate frame per second
        cTime = time.time()
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
#   i do not know why but this line is neccessary
    if cv2.waitKey(1) == 1000:  # esc for quit
        pass
#   end the loop when mainwindow is closed
    if QWidget.isHidden(mainWindow) == True:  # esc for quit
        break
app.quit()
