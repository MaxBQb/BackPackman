'''
BackPackMan v0.0.1 initial
'''
import ctypes

from classes.bp_rooms import *

if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    g = Game(840, 750)
    g.start(Menu(g))
