'''
BackPackMan v0.0.1 initial
'''
from classes.bp_main import *

if __name__ == '__main__':
    g = Game(840, 750)
    g.start(Menu(g))
