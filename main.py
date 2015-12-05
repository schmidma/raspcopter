#!/usr/bin/env python3
# coding: utf-8

##########################################
# MAIN.py - Hauptklasse
##########################################

from gamepad import Gamepad
from motor import Motor
from gui import Gui
from gyro import Gyro

from pygame.locals import *
import sys, os, time, pygame, curses, getopt

class Main():
    def __init__(self, DEBUG, fps, stick_sens):
        self.DEBUG = DEBUG
        self.max_fps = fps
        self.stick_sens = stick_sens
        
        pygame.init()
        
        self.clock = pygame.time.Clock()
    
        self.run = True
        self.started = False
    
        self.main_throttle = 0
        self.throttle = [0,0,0,0]

        self.holdPosition = 0
        self.holdHeight = 0
        self.isGamepad = 1
        
        self.gamepad = Gamepad()
        self.gamepad_axis = [0,0,0]
        self.gamepad_throttle = 0
        
        self.gyro = Gyro()
        self.gyro_axes = [0,0,0]
        self.gyro_throttle = [0,0,0]
        
        self.m1 = Motor(15)
        self.m2 = Motor(27)
        self.m3 = Motor(10)
        self.m4 = Motor(7)
        
        self.motors = [self.m1, self.m2, self.m3, self.m4]
        
        if self.DEBUG:
            self.gui = Gui()
        
        if self.DEBUG:
            self.gui.showMessage("Press 'start'-Button to start!")
        
        self.loop()
        
    def eventHandler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                if self.DEBUG:
                    curses.endwin()
                sys.exit()
            elif event.type == JOYBUTTONDOWN:
                self.gamepad.handleButtonDown(event.button)
            elif event.type == JOYBUTTONUP:
                self.gamepad.handleButtonUp(event.button)
        
    def getGamepadValues(self):
        self.gamepad_throttle = self.gamepad.getThrottle()
        self.gamepad_axis = self.gamepad.getAxis()
        
        if self.gamepad.isCalib:
            self.gyro.calibrateGyro()
        
    def start_motors(self):
        if self.DEBUG:
            self.gui.hideMessage()
            self.gui.showMessage("Calibrate Throttle!")
        
        while self.gamepad.getThrottle()<=50:
            pygame.event.pump()
        
        while self.gamepad.getThrottle()!=0:
            pygame.event.pump()
        
        for m in self.motors:
            m.start()
        
        self.gyro.calibrateGyro()
        
        self.started = True
        
        if self.DEBUG:
            self.gui.hideMessage()
    
    def stop_motors(self):
        for m in self.motors:
            m.stop()
        self.started = False
        
        if self.DEBUG:
            self.gui.showMessage("Press 'start'-Button to start!")
        
    def changeMotorSpeed(self):
        self.throttle = [0,0,0,0]
        self.getGamepadValues()
        #self.gyro_axes = self.gyro.getGyroValues()
        
        if (self.gamepad.isHoldHeight):
            pass
        
        if (self.gamepad.isHoldPosition):
            pass
        
        if (self.gamepad.isGyro):
            self.gyro.gyroCalculation(self.clock.get_time())
            
            #Accel-Motor-Steuereung
            self.throttle[0] += self.gyro.gyro_diff[0]
            self.throttle[1] += self.gyro.gyro_diff[0]
            self.throttle[2] -= self.gyro.gyro_diff[0]
            self.throttle[3] -= self.gyro.gyro_diff[0]
    
            self.throttle[0] -= self.gyro.gyro_diff[1]
            self.throttle[1] += self.gyro.gyro_diff[1]
            self.throttle[2] += self.gyro.gyro_diff[1]
            self.throttle[3] -= self.gyro.gyro_diff[1]

        #Pad-Motor-Steuerung
        self.throttle[0] += -self.gamepad_axis[0]*self.stick_sens+self.gamepad.calibrationValues[0] + self.gamepad_axis[1]*self.stick_sens+self.gamepad.calibrationValues[1] - self.gamepad.calibrationValues[2]
        self.throttle[1] += -self.gamepad_axis[0]*self.stick_sens+self.gamepad.calibrationValues[0] - self.gamepad_axis[1]*self.stick_sens+self.gamepad.calibrationValues[1] + self.gamepad.calibrationValues[2]
        self.throttle[2] += +self.gamepad_axis[0]*self.stick_sens+self.gamepad.calibrationValues[0] - self.gamepad_axis[1]*self.stick_sens+self.gamepad.calibrationValues[1] - self.gamepad.calibrationValues[2]
        self.throttle[3] += +self.gamepad_axis[0]*self.stick_sens+self.gamepad.calibrationValues[0] + self.gamepad_axis[1]*self.stick_sens+self.gamepad.calibrationValues[1] + self.gamepad.calibrationValues[2]
        
        self.throttle = [int(self.gamepad_throttle+self.throttle[i]) for i in range(4)]
        
        for i in range(4):
            if self.throttle[i] > 100:
                self.throttle[i] = 100
            elif self.throttle[i] < 0:
                self.throttle[i] = 0
            self.motors[i].setW(self.throttle[i])
            
    def loop(self):
        while self.run:
            self.clock.tick(self.max_fps)
            
            pygame.event.pump()
            self.eventHandler()
            
            if self.DEBUG:
                self.gui.guiTick(self.clock.get_fps(), self.throttle, self.gamepad.isStart, self.gamepad.isHoldHeight, self.gamepad.isHoldPosition, self.gamepad.isGyro)
            
            if self.gamepad.isStart:
                if not self.started:
                    self.start_motors()
                self.changeMotorSpeed()
            else:
                if self.started:
                    self.stop_motors()
                    