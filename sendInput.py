
from time import sleep
import win32gui, win32ui, win32con
from pynput.keyboard import Key, Controller

def main():

    keyboard = Controller()

    # window_name = "Untitled - Notepad"
    # hwnd = win32gui.FindWindow(None, window_name)
    # hwnd = get_inner_windows(hwnd)['RichEditD2DPT']
    # win = win32ui.CreateWindowFromHandle(hwnd)
    # list_window_names()

    global mario_win_name
    mario_win_name = "wrong"
    get_mario_name()    
    print(mario_win_name)

    # mario_name = "Dolphin 5.0-17970 | JITa64 DC | OpenGL | HLE | FPS: 60 - VPS: 60 - 100% | Mario Kart Wii (RMCE01)"
    hwnd = win32gui.FindWindow(None, mario_win_name)
    win = win32ui.CreateWindowFromHandle(hwnd)

    # list_window_names()
    keyboard.press('a')

    while True:
        sleep(1)
        keyboard.press('a')
        sleep(0.1)
        keyboard.release('a')
    # win.SendMessage(keyboard.press('a"'))
    # win.SendMessage(keyboard.release('a"'))
    # win.SendMessage(win32con.WM_CHAR, ord('a'), 0)
    # sleep(0.01)
    # win.SendMessage(win32con.WM_CHAR, ord('B'), 0)

def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hex(hwnd), '"' + win32gui.GetWindowText(hwnd) + '"')
    win32gui.EnumWindows(winEnumHandler, None)

def get_mario_name():
    def findMarioOne(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            curr = win32gui.GetWindowText(hwnd)
            substring = curr[0: 21]
            mario_name = "Dolphin 5.0-17970 | JITa64 DC | OpenGL | HLE | FPS: 60 - VPS: 60 - 100% | Mario Kart Wii (RMCE01)"
            mario_sub = mario_name[0: 21]
            if substring == mario_sub:
                global mario_win_name
                mario_win_name = curr
    win32gui.EnumWindows(findMarioOne, None)
    

def get_inner_windows(whndl):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = hwnd
        return True
    hwnds = {}
    win32gui.EnumChildWindows(whndl, callback, hwnds)
    print(hwnds)
    return hwnds

main()