from easyocr import easyocr
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.button import MDFlatButton
from kivy.uix.label import Label
import cv2
from kivy.uix.screenmanager import ScreenManager, Screen
import re

class Camera(MDApp):
    def build(self):
        self.load_kv('layout.kv')
        return sm

class CameraClick(BoxLayout, Screen):
    def capture(self):
        camera = self.ids['camera']
        camera.export_to_png("saved_img.jpg")
        print("Captured")

class ImageScreen(BoxLayout, Screen):

    def testrun(self):
        pass



class CodeEnterScreen(BoxLayout, Screen):
    pass

class CodeSentScreen(Screen):
    pass


# Create the screen manager
sm = ScreenManager()
sm.add_widget(CameraClick(name='Camera'))
sm.add_widget(ImageScreen(name='Image'))
sm.add_widget(CodeEnterScreen(name='CodeEntry'))
sm.add_widget(CodeSentScreen(name='CodeSent'))

if __name__ == '__main__':
    Camera().run()