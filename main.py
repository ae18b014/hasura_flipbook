from sys import argv
import imageio
from PIL import Image
import numpy as np

keywords={"start","end","combine"}
extensions=('.jpg','.jpeg','.png')
# import parser
def scanner(text):
	text = text.split('\n')
	flag = 0
	markers = [-1,len(text)]
	for it,lin in enumerate(text):
		if lin == "start":
			flag = 1
			markers[0] = it
		elif lin == "end":
			flag = 2
			markers[1] = min(it,markers[1])
		if flag == 1:
			tokens = lin.split()
			for t in tokens:
				if t in keywords:
					continue
				elif t.isdigit():
					continue
				elif t.endswith(extensions):
					continue
				else:
					print ("Unrecognized character " + str(t) + " on line " + str(it))
					return 0,markers
	if flag == 0:
		return 0,markers
	return 1,markers

extensions=('.jpg','.jpeg','.png')

def parser(text, markers):
	text = text.split('\n')[markers[0]:markers[1]+1]
	if text[0] != "start":
		print ("Syntax error: Code must start with keyword 'start'")
		return [0,0]
	elif text[-1] != "end":
		print ("Syntax error: Code must end with keyword 'end'")
		return [0,0]
	frame_img=[]
	for it,lin in enumerate(text[1:-1]):
		tokens = lin.split()
		#standard command
		if len(tokens) == 3:
			if tokens[0].isdigit() and tokens[1].isdigit() and tokens[2].endswith(extensions):
				if int(tokens[0]) > int(tokens[1]):
					print ("Syntax error on line " + str(it) + ": starting frame should be lesser than or equal to ending frame.")
					return [0,0]
				frame_img.append([int(tokens[0]),int(tokens[1]),tokens[2]])
				continue
			else:
				print ("Syntax error on line " + str(it))
				return [0,0]
		#combine command, doing only for 2 pics
		elif len(tokens) == 6:
			if tokens[0].isdigit() and tokens[1].isdigit() and tokens[2] == "combine" and tokens[3].isdigit():
				
				if int(tokens[0]) > int(tokens[1]):
					print ("Syntax error on line " + str(it) + ": starting frame should be lesser than or equal to ending frame.")
					return [0,0]

				framearr = []
				framearr.append(int(tokens[0]))
				framearr.append(int(tokens[1]))
				for i in range(1, int(tokens[3])+1):
					if tokens[3+i].endswith(extensions):
						framearr.append(tokens[3+i])
					else:
						print ("Syntax error on line " + str(it) + ": pls use images with the extensions " + extensions)
						return [0,0]
				frame_img.append(framearr)
				continue
			else:
				print ("Syntax error on line " + str(it))
				return [0,0]
		else:
			print ("Syntax error on line " + str(it) + ": too many or too few arguments in a single line")
			return [0,0]
	return [1, frame_img]


class FlipBook :
    """ Parent class which will contain all required helper functions and 
    store necessary variables to produce required flipbook """
    
    def __init__(self):
        self.frame_list = []
        self.dim = 720
        self.blank = np.zeros([self.dim,self.dim,3],dtype=np.uint8)
        self.blank.fill(0)
        
    def generate_gif(self, frames):
        for frame in frames:
            startFrame = frame[0]
            endFrame = frame[1]
            # print (frame, len(frame))
            if len(frame) == 3: # standard appending
                imageName = frame[2]
            else:
                imageName = self.combine_images(frame[2:])
            self.add_image_to_frame_list(startFrame, endFrame, imageName)

        imageio.mimsave('flipbook.gif', self.frame_list)
        print("GIF named flipbook.gif has been generated")
        
    def combine_images(self, imageList):
        #assume 2 images being horizontally concatenated
        n = len(imageList)
        im1 = Image.open(imageList[0])
        im2 = Image.open(imageList[1])
        # dst = Image.new('RGB', (im1.width + im2.width, min(im1.height, im2.height)))
        dst = Image.new('RGB', (self.dim, self.dim))
        dst.paste(im1, (0, 0))
        # dst.paste(im2, (im1.width, (im1.height - im2.height) // 2))
        dst.paste(im2, (im1.width, 0))
        return dst

    def add_image_to_frame_list(self,startFrame, endFrame, imageName):
        """ add other params/functions to do resizing/positioning etc """       
        for i in range(startFrame-1, endFrame-1):
            try:
                # image = imageio.imread(imageName)
                im = Image.open(imageName)
                im = im.resize((720, 720))
                self.frame_list.append(im)
                # self.frame_list.append(im)

            except:
                print (imageName, " not found.")
                # BufferedImage bi= new BufferedImage(320,240,BufferedImage.TYPE_BYTE_GRAY);
                im=self.blank
                self.frame_list.append(im)


    def parse_input(self, text, markers):
        code, frames = parser(text, markers)
        if code:
            self.generate_gif(frames)
        else:
            exit()

    def scan_input(self, text):
        code, markers = scanner(text)
        if code:
            self.parse_input(text, markers)
        else:
            exit()

def main():
    
    #read input file contents
    ipfile = input()
    if ipfile.endswith(".flip") is False:
        print ("Input a .flip file")
        exit()
    file_obj = open(ipfile,"r")
    if file_obj.mode=="r":
        text = file_obj.read()
        print (text)
        FB = FlipBook()
        FB.scan_input(text)



if __name__ == '__main__':
    main()