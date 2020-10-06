from easyocr import easyocr
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import cv2
from kivy.uix.screenmanager import ScreenManager, Screen
import re
from kivy.clock import Clock, mainthread

Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    spacing: 20
    Image:
    	source: 'Bentleylogo.png'
    	size: self.texture_size
    Camera:
        id: camera
        resolution: (640, 640)
        size_hint: (1,4)
        play: True
    
    Button:
        text: "Capture"
        text_color: 0, 0, 1, 1
        size_hint_y: None
        height: '48dp'
        width: '48dp'
        on_press: 
        	root.capture()
        on_release:
            root.manager.current = "Image"
        	root.manager.transition.direction = 'up'
    Image:
    	source: 'Degouldlogo.png'
    	size: self.texture_size


<ImageScreen>
	orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    on_enter: root.testrun()        
    Image:
    	source: 'Bentleylogo.png'
    	size: self.texture_size
    Label:
		text: "Is this code correct?"
		color: 0, 0, 0, 1
	Label:
	    id: my_code
	    text: "0000000"
	    font_size: 32
		color: 0, 0, 0, 1	
	Button:
    	text: 'Yes'
        size_hint_y: None
        height: '48dp'
        on_release:
        	root.manager.transition.direction = 'up'
        	root.manager.current = 'CodeSent'
	Button:
    	text: 'No'
        size_hint_y: None
        height: '48dp'
        on_release:
        	root.manager.transition.direction = 'up'
        	root.manager.current = 'CodeEntry'
    
    Image:
    	source: 'Degouldlogo.png'
    	size: self.texture_size

<CodeEnterScreen>
	orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Image:
    	source: 'logos.png'
    	size: self.texture_size
    Label:
		text: "Enter Code"
		height: '48dp'
		color: 0, 0, 0, 1
    TextInput:
    	height: '48dp'
    	id: code_input
    	multiline: False
    	focus: True

	Button:
		height: '48dp'
		text: "submit"
    	on_release:
        	root.manager.transition.direction = 'up'
        	root.manager.current = 'CodeSent'
    Image:
    	source: 'Degouldlogo.png'
    	size: self.texture_size

<CodeSentScreen>
	orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    on_enter: root.manager.current = 'Camera'        
    Label:
		text: "Code Sent"
		color: 0, 0, 0, 1

    


''')

class LoadScreen(Screen):
    def on_enter(self, *args):
        if self.manager.current != "loading.png":
            Clock.schedule_once(self.callbackfun, 0.5)

class CameraClick(BoxLayout, Screen):
    def capture(self):
        camera = self.ids['camera']
        camera.export_to_png("saved_img.jpg")
        print("Captured")

class ImageScreen(BoxLayout, Screen):

    def testrun(self):
        reader = easyocr.Reader(['en'])
        img = cv2.imread('saved_img.jpg')
        result = reader.readtext(img, detail=0)
        print(result)
        for i in result:
            checkspace = re.sub(r"\s+", "", i)
            checkRL = re.sub(r"RL-", "", checkspace)
            with open('codelist.txt') as f:
                datafile = f.readlines()
                for line in datafile:  # <--- Loop through each line
                    if checkRL in line:
                        self.ids.my_code.text = str(checkRL)

class CodeEnterScreen(BoxLayout, Screen):
    pass

class CodeSentScreen(Screen):
    pass


class OCRCamera(App):
    def build(self):
        return sm

# Create the screen manager
sm = ScreenManager()
sm.add_widget(CameraClick(name='Camera'))
sm.add_widget(ImageScreen(name='Image'))
sm.add_widget(CodeEnterScreen(name='CodeEntry'))
sm.add_widget(CodeSentScreen(name='CodeSent'))


if __name__ == '__main__':
    OCRCamera().run()