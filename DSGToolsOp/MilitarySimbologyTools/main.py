# -*- coding: utf-8 -*-
from .view.militarySimbologyInterface import MilitarySimbologyInterface

class Main:
    def __init__(self):
        '''Construtor'''
        militarySimbologyInterface = MilitarySimbologyInterface()
        self.setFrame(militarySimbologyInterface)

    def setFrame(self, f):
        '''Metodo para definir a interface principal do tipo Dock'''
        self.frame = f

    def getFrame(self):
        '''Metodo para obter a interface principal do tipo Dock'''
        return self.frame
