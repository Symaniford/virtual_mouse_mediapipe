FILES
logo_hand.ico: icon of the program's window
logo_hand.png: showed in the window
logo_mediapipe.png: showed in the window
virtual_mouse.py: origin py file written in python
README.txt: *README.txt 

PYINSTALLER COMMAND
pyinstaller -F -w -i \hand.ico virtual_mouse.py --add-data="\mediapipe\modules;mediapipe\modules" --add-data="\logo_mediapipe.png;\" --add-data="\logo_hand.ico;\" --add-data="\logo_hand.png;\"

HOW TO USE THE PROGRAM
Click "CAMERA SWITCH" if you have two cameras and you want use one of them
Click "SHOW IMAGE" to use your camera to capture image
Click "IMAGE FLIP" if you think your image need a flip
Click "CURSOR MOVE"  and then you can use your index finger to control the cursor
	You can slide the "STABILITY" to change the stability of cursor. 
Click "CLICK MODE" and (CURSOR MOVE is still working) :
	when you stick out your index finger and middle finger, the mouse will go on a left click
	when you stick out your index finger and little finger, the mouse will go on a right click
	when you stick out your index finger and thumb, and they are orthogonal, the mouse will press until not orthogonal. p.s: you cannot use this to drag the virtual_mouse window for it will pause the image.
	There is text below the image showing last mouse event.

PAY ATTENTION
Better to check if virtual_mouse.exe are running after you close the window.

github :virtual_mouse

