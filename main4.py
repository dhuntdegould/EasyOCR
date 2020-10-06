from easyocr import easyocr
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import cv2
from kivy.uix.screenmanager import ScreenManager, Screen
import re
from kivy.clock import Clock, mainthread
import numpy as np
from imutils.object_detection import non_max_suppression

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

net = cv2.dnn.readNet("frozen_east_text_detection.pb")

def horizontal_text_detector(image):
	orig = image
	(H, W) = image.shape[:2]
	(newW, newH) = (640, 624)
	rW = W / float(newW)
	rH = H / float(newH)

	image = cv2.resize(image, (newW, newH))
	(H, W) = image.shape[:2]

	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]

	blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
		(123.68, 116.78, 103.94), swapRB=True, crop=False)

	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)

	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	for y in range(0, numRows):

		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability, ignore it
			if scoresData[x] < 0.5:
				continue

			# compute the offset factor as our resulting feature maps will
			# be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)

			# extract the rotation angle for the prediction and then
			# compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)

			# use the geometry volume to derive the width and height of
			# the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# compute both the starting and ending (x, y)-coordinates for
			# the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# add the bounding box coordinates and probability score to
			# our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	boxes = non_max_suppression(np.array(rects), probs=confidences)

	for (startX, startY, endX, endY) in boxes:

		startX = int(startX * rW)
		startY = int(startY * rH)
		endX = int(endX * rW)
		endY = int(endY * rH)
		boundary = 2
		pretext = orig[startY-boundary:endY+boundary, startX - boundary:endX + boundary]
		pretext = cv2.cvtColor(pretext.astype(np.uint8), cv2.COLOR_BGR2GRAY)
		pretext = cv2.medianBlur(pretext, 5)
		pretext = cv2.adaptiveThreshold(pretext, 245, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 115, 1)
		cv2.imshow("preprocess", pretext)
		cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 3)
		orig = cv2.putText(orig, (endX,endY+5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
		return orig

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
            checkcode = re.sub(r"\s+", "", i)
            with open('codelist.txt') as f:
                datafile = f.readlines()
                for line in datafile:  # <--- Loop through each line
                    if checkcode in line:
                        self.ids.my_code.text = str(checkcode)


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