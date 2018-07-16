# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 16:21:12 2017

@author: js22g12
"""

import os
os.chdir('..')
import sys
import copy
import numpy as np
from scipy.special import binom
from scipy.interpolate import interp1d
from AmpScan.core import AmpObject
from AmpScan.ampVis import qtVtkWindow
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QFileDialog, QWidget, QSlider,
                             QGroupBox, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSignal, Qt


class GUI(QMainWindow):
    """
    Numpy style docstring

    """
    def __init__(self, parent=None):
        super(GUI, self).__init__()
        self.points = np.zeros([6])
        self.AmpObj = None
        self.redFunc = None
        self.scaleIdx = 0
        self.mainWidget = QWidget()
        self.limbWidget = qtVtkWindow()
        self.limbRen = self.limbWidget._RenderWindow
        self.limbRen.setBackground([0.9,0.9,0.9])
        self.socketWidget = qtVtkWindow()
        self.socketRen = self.socketWidget._RenderWindow
        self.socketRen.setBackground([0.9,0.9,0.9])
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        self.Layout = QGridLayout()
        self.sl = self.sliders()
        self.Layout.addWidget(self.limbWidget, 0, 0, -1, 1)
        self.Layout.addWidget(self.sl, 0, 1, 1, 1)
        self.Layout.addWidget(self.socketWidget, 1, 1, 3, 1)
        self.mainWidget.setLayout(self.Layout)
        self.setWindowTitle("AmpScan Visualiser")
        self.resize(1200, 800)
        self.show()

    def plotPress(self):
        """
        Numpy style docstring

        """
        for i, s in enumerate(self.sliders):
            self.points[i] = s.value()/100
        if self.AmpObj is None:
            return
        self.scale(self.points[3:5])
        weights = np.array([1.0, 5.0, 1.0])
        bPoints = np.array([[0.0, self.points[2]],
                            [0.5, self.points[1]],
                            [1.0, self.points[0]]])
        bezier = self.bSpline(bPoints, weights, self.socket.vert[:, 2])
        self.socket.values[:] = bezier[:, 1] * 6
        self.socket.actor.setValues(self.socket.values)
        self.AmpObj.surrPred(self.points, norm=False)
        self.AmpObj.actor.setValues(self.AmpObj.values)  
        self.limbRen.Render()
        self.socketRen.Render()
    
    def scale(self, var):
        """
        Numpy style docstring

        """
        var = (var * 0.3) - 0.15
        cent = [85.93, 75.53, 0.0]
        height = 150.0
#        for p in [self.AmpObj, self.socket]:
        for p in [self.AmpObj,]:
            if self.scaleIdx == 0:
                p.nodes = p.vert.copy()
                p.idx = p.nodes[:, 2] < height
            nodes = p.nodes - cent
            rad = np.sqrt(nodes[:,0]**2 + nodes[:,1]**2)
            the = np.arctan2(nodes[:,1], nodes[:,0])
            weights = np.array([1.0, 5.0, 5.0, 1.0])
            bPoints = np.array([[0.0, 1 + var[1]],
                                [0.3, 1 + 0.9*var[1]],
                                [0.6, 1 + 0.2*var[1]],
                                [1.0, 1 + 0.1*var[1]]])
            #bezier = self.bSpline(bPoints, weights, nodes[p.idx, 2])
            bezier = self.bSpline(bPoints, weights, nodes[:, 2])
            #rad[p.idx] = rad[p.idx] * bezier[:, 1]
            rad[:] *= bezier[:, 1]
            x = rad * np.cos(the)
            y = rad * np.sin(the)
            nodes[:, 0] = x + cent[0]
            nodes[:, 1] = y + cent[1]
            # Length of the limb 
            nodes[p.idx, 2] += (nodes[p.idx, 2]-height) * var[0]
            p.vert[:, :] = nodes
            p.actor.setVert(p.vert)
            p.actor.points.Modified()
        self.scaleIdx = 1
                
        
        
    def sliders(self):
<<<<<<< Updated upstream
        """
        Numpy style docstring

        """
        variables = ['Proximal Reduction', 'Mid Reduction', 'Distal Reduction',
                     'Residuum Length', 'Residuum Bulk', 'Tissue Stiffness']
        labels = [[' 0', '3', '6 '], [' 0', '3', '6 '], [' 0', '3', '6 '],
                  ['-15', '0', '+15'], ['-15', '0', '+15'], ['-10', '0', '+10']]
=======
        variables = ['Proximal Reduction, %', 'Mid Reduction, %', 'Distal Reduction, %',
                     'Residuum Length, %', 'Residuum Bulk, %', 'Tissue Stiffness, kPa']
        labels = [['0', '3', '6'], ['0', '3', '6'], ['0', '3', '6'],
                  ['-15', '0', '+15'], ['-15', '0', '+15'], ['30', '55', '80']]
>>>>>>> Stashed changes
        values = [0, 0, 0, 50, 50, 50]
#        values = values[:5]
#        labels = labels[:5]
#        variables = variables[:5]
#        variables = ['Proximal Reduction', 'Mid Reduction', 'Distal Reduction']
#        values = [0, 0, 0]
        groupBox = QGroupBox('Model Variables')
        f = QFont("Arial", 12)
        groupBox.setFont(f)
        box = QGridLayout()
        self.sliders = []

        for lab, v, (i, t) in zip(labels, values, enumerate(variables)):
            tx = QLabel(t)
            f = QFont("Arial", 12)
            tx.setFont(f)
            tx.setAlignment(Qt.AlignVCenter)
            box.addWidget(tx, i*3, 0, 3, 1)   
            self.sliders.append(QSlider(Qt.Horizontal))
            self.sliders[-1] = QSlider(Qt.Horizontal)
            self.sliders[-1].setFocusPolicy(Qt.StrongFocus)
            self.sliders[-1].setTickPosition(QSlider.TicksBothSides)
            self.sliders[-1].setTickInterval(25)
            self.sliders[-1].setSingleStep(1)
            self.sliders[-1].setMinimum(0)
            self.sliders[-1].setMaximum(100)
            self.sliders[-1].setValue(v)
            self.sliders[-1].valueChanged.connect(self.plotPress)
            box.addWidget(self.sliders[-1], i*3, 1, 2, 3)
            align = [Qt.AlignLeft, Qt.AlignHCenter, Qt.AlignRight]
            for (j, l), a in zip(enumerate(lab), align):
                lab = QLabel(l)
                lab.setAlignment(a)
                f = QFont("Arial", 10)
                lab.setFont(f)
                box.addWidget(lab, (i*3) + 2, j + 1, 1, 1)
        groupBox.setLayout(box)
        return groupBox
    
    def bSpline(self, points, weights, t):
        zMin = t.min()
        zRange = t.max() - zMin
        t = (t - zMin)/zRange
        num = np.zeros([t.shape[0], 2])
        dem = np.zeros([t.shape[0], 2])
        n = points.shape[0] - 1
        for (i, point), weight in zip(enumerate(points), weights):
            biCoeff = binom(n, i)
            num = num + ((biCoeff*t**i) * ((1-t)**(n-i)))[:, None] * point * weight
            dem = dem + ((biCoeff*t**i) * ((1-t)**(n-i)))[:, None] * weight
        return num/dem


    def chooseOpenFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                                 filter="Surrogate Model (*.npy)")
        data = np.load(self.fname[0]).item()
        self.AmpObj = AmpObject(data['limb'], stype='FE')
        #self.AmpObj.centre()
        self.AmpObj.addSurrogate(data['surr'])
        self.socket = AmpObject(data['socket'])
        c1 = [212.0, 221.0, 225.0]
        c2 = [31.0, 73.0, 125.0]
        CMap = np.c_[[np.linspace(st, en) for (st, en) in zip(c1, c2)]]
        CMap = np.transpose(CMap)/255.0
        self.AmpObj.addActor(CMap=CMap, bands = 10)
        self.AmpObj.actor.setNorm()
        self.AmpObj.actor.setScalarRange([0, 60])
        self.socket.addActor(CMap=CMap, bands = 128)
        self.socket.actor.setNorm()
        self.socket.actor.setScalarRange([0, 6])
        self.plotPress()
        self.limbRen.renderActors([self.AmpObj.actor], shading=False)
        self.limbRen.setScalarBar(self.AmpObj.actor, title='Interfacial\nPressure, kPa')
        self.limbRen.setView()
        self.socketRen.renderActors([self.socket.actor,], shading=False)
        self.socketRen.setScalarBar(self.socket.actor, title = 'Socket\nRectification, %')
        self.socketRen.setView()


    def createActions(self):
        """
        Numpy style docstring

        """
        self.openFile = QAction(QIcon('open.png'), 'Open', self,
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)
        




if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainWin = GUI()
    mainWin.show()
    sys.exit(app.exec_())