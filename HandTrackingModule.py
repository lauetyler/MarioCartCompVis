
import cv2
import mediapipe as mp
import time
from pynput.keyboard import Key, Controller
from time import sleep
import math
import vgamepad


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionConf=0.5, trackConf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConf = detectionConf
        self.trackConf = trackConf

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, 1, self.detectionConf, self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        if img is None:
            return img
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def getHandLabels(self, img):
        handsType = []
        numHands = 0
        if self.results.multi_handedness:
            numHands = len(self.results.multi_handedness)
            for hand in self.results.multi_handedness:
                handsType.append(hand.classification[0].label)

        return handsType, numHands

    def findPosition(self, img, handsType, numHands, draw=True):
        lmListLeft = []
        lmListRight = []

        if (numHands == 0):
            return lmListLeft, lmListRight

        if self.results.multi_hand_landmarks:
            for hand, handType in zip(self.results.multi_hand_landmarks, handsType):
                if (handType == "Right"):
                    for id, lm in enumerate(hand.landmark):

                        h, w, c = img.shape
                        cx, cy = int(lm.x*w), int(lm.y*h)
                        lmListRight.append([id, cx, cy])
                        if draw:
                            cv2.circle(img, (cx, cy), 7,
                                       (0, 255, 0), cv2.FILLED)
                if (handType == "Left"):
                    for id, lm in enumerate(hand.landmark):

                        h, w, c = img.shape
                        cx, cy = int(lm.x*w), int(lm.y*h)
                        lmListLeft.append([id, cx, cy])
                        if draw:
                            cv2.circle(img, (cx, cy), 7,
                                       (255, 0, 0), cv2.FILLED)

        return lmListLeft, lmListRight


def readInput(lmListLeft, lmListRight, keyboard, gamepad, img):
    # Get Scalar based on right hand
    valy = lmListRight[5][2] - lmListRight[17][2]
    valx = lmListRight[5][1] - lmListRight[17][1]
    rightScaler = math.sqrt((valy**2) + (valx**2))
    
    valy = lmListLeft[5][2] - lmListLeft[17][2]
    valx = lmListLeft[5][1] - lmListLeft[17][1]
    leftScaler = math.sqrt((valy**2) + (valx**2))
    
    # Check Steering
    val = lmListLeft[5][2] - lmListRight[5][2]
    analog = 50

    if val < -50:
        # keyboard.release('f')
        # keyboard.press('g')

        if (val < -250):
            val = -250
        analog = int(((val + 50) * -1)/2)
        for i in range(analog * 2):
            cv2.putText(img, str("."), (10 + i, 200),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        analog = float((analog/100))
        gamepad.left_joystick_float(x_value_float=analog, y_value_float=0.0)
        gamepad.update()

    elif val > 50:

        if (val > 250):
            val = 250
        analog = int(((val - 50)/2))
        for i in range(analog * 2):
            cv2.putText(img, str("."), (10 + i, 200),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
            
        analog = float((analog/100) * -1)

        gamepad.left_joystick_float(x_value_float=analog, y_value_float=0.0)
        gamepad.update()
        
    else:
        gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        gamepad.update()


    # Check B button (Left hand thumb)
    valy = lmListLeft[6][2] - lmListLeft[4][2]
    valx = lmListLeft[6][1] - lmListLeft[4][1]
    val = math.sqrt((valy**2) + (valx**2))
    val = (val * 100)/leftScaler
    print(val)
    
    if val < 70:
        # keyboard.press('b')
        gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        cv2.putText(img, str("b"), (50, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    else:
        # keyboard.release('b')
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        cv2.putText(img, str("b"), (50, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    # Check A button (Right hand thumb)
    valy = lmListRight[6][2] - lmListRight[4][2]
    valx = lmListRight[6][1] - lmListRight[4][1]
    val = math.sqrt((valy**2) + (valx**2))
    val = (val * 100)/rightScaler
    if val < 70:
        # keyboard.press('a')
        gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        cv2.putText(img, str("a"), (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    else:
        # keyboard.release('a')
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        cv2.putText(img, str("a"), (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    # Check X button (hand nuckles together)
    valx = lmListRight[10][1] - lmListLeft[10][1]
    valy = lmListRight[10][2] - lmListLeft[10][2]
    val = math.sqrt((valy**2) + (valx**2))
    val = (val * 100)/rightScaler
    if val < 70:
        gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        cv2.putText(img, str("super"), (10, 160),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    else:
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        cv2.putText(img, str("super"), (10, 160),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

def main():

    keyboard = Controller()
    gamepad = vgamepad.VX360Gamepad()

    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        if img is None:
            continue
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        handsType, numHands = detector.getHandLabels(img)
        lmListLeft, lmListRight = detector.findPosition(
            img, handsType, numHands)

        if len(lmListLeft) != 0 and len(lmListRight) != 0:
            readInput(lmListLeft, lmListRight, keyboard, gamepad, img)

        # show FPS in top left
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()