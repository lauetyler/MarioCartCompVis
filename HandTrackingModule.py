
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

    #function to draw hands in image
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

    #gets specific hand points
    def getHandLabels(self, img):
        handsType = []
        numHands = 0
        if self.results.multi_handedness:
            numHands = len(self.results.multi_handedness)
            for hand in self.results.multi_handedness:
                handsType.append(hand.classification[0].label)

        return handsType, numHands

    #function to return a list of points for both left hand and right
    def findPosition(self, img, handsType, numHands, draw=True):
        lmListLeft = []
        lmListRight = []

        #if no hands are found
        if (numHands == 0):
            return lmListLeft, lmListRight

        if self.results.multi_hand_landmarks:
            for hand, handType in zip(self.results.multi_hand_landmarks, handsType):

                #if right hand, draw green points
                if (handType == "Right"):
                    for id, lm in enumerate(hand.landmark):

                        h, w, c = img.shape
                        cx, cy = int(lm.x*w), int(lm.y*h)
                        lmListRight.append([id, cx, cy])
                        if draw:
                            cv2.circle(img, (cx, cy), 7,
                                       (0, 255, 0), cv2.FILLED)

                #if left hand, draw blue points
                if (handType == "Left"):
                    for id, lm in enumerate(hand.landmark):

                        h, w, c = img.shape
                        cx, cy = int(lm.x*w), int(lm.y*h)
                        lmListLeft.append([id, cx, cy])
                        if draw:
                            cv2.circle(img, (cx, cy), 7,
                                       (255, 0, 0), cv2.FILLED)

        #return updated lists of hand points
        return lmListLeft, lmListRight

pastInTime = 0


#Function to read one hand for menu input
def readRightHand(lmListRight, keyboard, gamepad, img, cTime):

    # Get Scalar based on right hand
    valy = lmListRight[5][2] - lmListRight[17][2]
    valx = lmListRight[5][1] - lmListRight[17][1]
    rightScaler = math.sqrt((valy**2) + (valx**2))

    if rightScaler == 0:
        return
    
    total = 0
    # Get total distance between fingers start and fingers end

    # Thumb distace
    valx = (lmListRight[6][1] - lmListRight[4][1])/rightScaler
    valy = (lmListRight[6][2] - lmListRight[4][2])/rightScaler
    thumb = int(100 * math.sqrt((valy**2) + (valx**2)))

    # Pointer distance
    valx = (lmListRight[5][1] - lmListRight[8][1])/rightScaler
    valy = (lmListRight[5][2] - lmListRight[8][2])/rightScaler
    pointer = int(100 * math.sqrt((valy**2) + (valx**2)))

    # Middle Finger
    valx = (lmListRight[9][1] - lmListRight[12][1])/rightScaler
    valy = (lmListRight[9][2] - lmListRight[12][2])/rightScaler
    middle = int(100 * math.sqrt((valy**2) + (valx**2)))

    # Ring Finger
    valx = (lmListRight[16][1] - lmListRight[13][1])/rightScaler
    valy = (lmListRight[16][2] - lmListRight[13][2])/rightScaler
    ring = int(100 * math.sqrt((valy**2) + (valx**2)))

    # Pinky
    valx = (lmListRight[20][1] - lmListRight[17][1])/rightScaler
    valy = (lmListRight[20][2] - lmListRight[17][2])/rightScaler
    pinky = int(100 * math.sqrt((valy**2) + (valx**2)))
    
    #time variable
    global pastInTime 
    

    #periodically release d-pad input
    if cTime - pastInTime > 0.1:
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        gamepad.update()


    total = thumb + pointer + middle + ring + pinky
    totalWOThumb = pointer + middle + ring + pinky


    # Check Right Index finger for D-Pad
    valx = (lmListRight[8][1] - lmListRight[5][1])/rightScaler
    valy = (lmListRight[8][2] - lmListRight[5][2])/rightScaler
    val = math.sqrt((valy**2) + (valx**2))

    intx = int(valx * 100)
    inty = int(valy * 100)
    intval = int(val)

    #meaning, total without thumb
    #so, our hand is in a fist position, and we are trying to press A or B
    if totalWOThumb < 150: 
        if cTime - pastInTime > 0.8:
            # print(totalWOThumb)
            # print(thumb)

            #if thumb is extended, press B
            if thumb > 80:
                gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
                gamepad.update()
                cv2.putText(img, str("b"), (50, 120),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
                print("B")
                pastInTime = cTime
            #if thumb is not extended, press A
            elif total < 160:
                gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
                gamepad.update()
                cv2.putText(img, str("a"), (10, 120),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
                print("A")
                pastInTime = cTime
            # print("other fingers: ", totalWOThumb)
            # print("thumb: ", thumb)
    # elif total < 160:
    #     if cTime - pastInTime > 0.8:
    #         gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
    #         gamepad.update()
    #         cv2.putText(img, str("a"), (10, 120),
    #                     cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    #         print("A")
    #         pastInTime = cTime
    
    #if we reach here, our hand is not in a fist position 
    #and we are presumably trying to navigate the menu using the D-Pad
    #Every "release_button" call is to ensure no continuing inputs from past gestures


    #Pointing Up
    elif inty < -120:
        if cTime - pastInTime > 0.8:
            print("Up")
            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            pastInTime = cTime

    #Pointing Down
    elif inty > 90:
        if cTime - pastInTime > 0.8:
            print("Down")
            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            pastInTime = cTime

    #Pointing Left
    elif intx < -130: 
        if cTime - pastInTime > 0.8:
            print("Left")
            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            pastInTime = cTime

    #Pointing Right
    elif intx > 80: 
        if cTime - pastInTime > 0.8:
            print("Right")
            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            pastInTime = cTime

    #Neutral hand, make no inputs
    else: 
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()


#Funcion to read both hands for driving inputs
def readBothHands(lmListLeft, lmListRight, keyboard, gamepad, img):
    # Get Scalar based on right hand
    valy = lmListRight[5][2] - lmListRight[17][2]
    valx = lmListRight[5][1] - lmListRight[17][1]
    rightScaler = math.sqrt((valy**2) + (valx**2)) 

    # Get Scalar based on left hand
    valy = lmListLeft[5][2] - lmListLeft[17][2]
    valx = lmListLeft[5][1] - lmListLeft[17][1]
    leftScaler = math.sqrt((valy**2) + (valx**2))

    if rightScaler == 0 or leftScaler == 0:
        return

    # Check Steering
    valy = (lmListLeft[5][2] * leftScaler) - (lmListRight[5][2] * rightScaler)
    valx = (lmListLeft[5][1] * leftScaler) - (lmListRight[5][1] * rightScaler)

    val = abs(math.atan(valy/valx) * (2/math.pi))
    if (valy > 0):
        val = val * -1

    val = int(val * 100)

    #We need to convert our value to between -1 and 1, for our x360 controller's left stick

    #Moving left on the analog stick
    if val < 0:
        analog = val * -1
        for i in range(analog * 2):
            cv2.putText(img, str("."), (10 + i, 220),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        analog = float((analog/100) * -1)
        gamepad.left_joystick_float(x_value_float=analog, y_value_float=0.0)
        gamepad.update()

    #Moving right on the analog stick
    elif val > 0:
        if (val > 250):
            val = 250
        analog = val
        for i in range(analog * 2):
            cv2.putText(img, str("."), (10 + i, 220),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        analog = float((analog/100))
        gamepad.left_joystick_float(x_value_float=analog, y_value_float=0.0)
        gamepad.update()

    #Not steering
    else:
        gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        gamepad.update()

    aPressed = False

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
        aPressed = True
    else:
        # keyboard.release('a')
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        cv2.putText(img, str("a"), (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        aPressed = False

    # Check B button (Left hand thumb)
    valy = lmListLeft[6][2] - lmListLeft[4][2]
    valx = lmListLeft[6][1] - lmListLeft[4][1]
    val = math.sqrt((valy**2) + (valx**2))
    val = (val * 100)/leftScaler
    # print(val)

    if val < 70:
        if aPressed:
            #Here, we know that if a is pressed then our right thumb is down
            #So, if the left the thumb also goes down, we are attempting to "trick", not brake

            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            gamepad.update()
            cv2.putText(img, str("trick"), (10, 160),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            cv2.putText(img, str("b"), (50, 120),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

        
        else:
            #But, if a is not pressed, then we are attempting to break
            # keyboard.press('b')
            gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
            gamepad.update()
            cv2.putText(img, str("b"), (50, 120),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

            gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            gamepad.update()
            cv2.putText(img, str("trick"), (10, 160),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
    else:
        # keyboard.release('b')
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        cv2.putText(img, str("b"), (50, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        gamepad.update()
        cv2.putText(img, str("trick"), (10, 160),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    # Check X button (hand knuckles together)
    valx = lmListRight[10][1] - lmListLeft[10][1]
    valy = lmListRight[10][2] - lmListLeft[10][2]
    val = math.sqrt((valy**2) + (valx**2))
    val = (val * 100)/rightScaler
    if val < 70:
        gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        cv2.putText(img, str("super"), (10, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    else:
        gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        cv2.putText(img, str("super"), (10, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)


def main():

    keyboard = Controller()
    #create our virtual x360 controller
    gamepad = vgamepad.VX360Gamepad()

    pTime = 0
    cTime = 0

    #Prepare webcam and handdetector
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

        #Driving, both hands
        if len(lmListLeft) != 0 and len(lmListRight) != 0:
            gamepad.reset()
            gamepad.update()
            readBothHands(lmListLeft, lmListRight, keyboard, gamepad, img)

        #Menu, one hand
        elif len(lmListRight) != 0 and len(lmListLeft) == 0:
            gamepad.reset()
            gamepad.update()
            readRightHand(lmListRight, keyboard, gamepad, img, cTime)

        #No hands
        else:
            gamepad.reset()
            gamepad.update()


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
