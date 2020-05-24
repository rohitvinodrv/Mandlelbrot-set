# This is the working version

from tkinter import *
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
import numpy
from mbset_v0 import generate, scale
from mbset_v1 import parallel_generate
from multiprocessing import Process

INIT_ITER = 300		# set to 300
ZOOM_FACTOR = 0.5


class WindowCanvas:
	def __init__(self, win):
		self.win = win
		self.zoom = 1
		self.w, self.h = win.winfo_screenwidth()-100, win.winfo_screenheight()-100
		self.op_range_x = (-2,1)
		self.op_range_y = (-1,1)
		self.itr = INIT_ITER
		first_image = self.make_image(self.itr, self.op_range_x, self.op_range_y)
		self.canvas = Label(win, width=self.h, height=self.h, image=first_image)
		self.canvas.pack(fill="both", expand="yes")
		self.canvas.configure(background='black')
		self.canvas.image = first_image
		self.load_icon = Image.open('loading.jpg').resize((200,200), Image.ANTIALIAS)	# loading symbol
		self.canvas.bind('<Double-Button-1>', self.double_click)
		self.canvas.bind('<Double-Button-3>', self.back)
		self.canvas.bind("<Button-2>", self.reset_image)
		self.num_back = 0																# this is used to check if its the first time back is called after double click
		self.steps = [(self.op_range_x, self.op_range_y)]
		# self.origins = []


	def make_image(self, itr, r_x, r_y):
		rows = 1920
		columns = 1080
		if itr > 1000:
			mat = parallel_generate(rows, columns, itr, r_x, r_y).T
		mat = numpy.zeros([rows, columns])
		mat = generate(mat, itr, r_x, r_y).T
		
		cmap = plt.cm.hot
		norm = plt.Normalize(vmin=mat.min(),vmax=mat.max())
		image = cmap(norm(mat))
		pilImage = Image.fromarray(numpy.uint8(image*255))
		imgWidth, imgHeight = pilImage.size
		if imgWidth > self.w or imgHeight > self.h:
		    ratio = min(self.w/imgWidth, self.h/imgHeight)
		    imgWidth = int(imgWidth*ratio)
		    imgHeight = int(imgHeight*ratio)
		    pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
		image = ImageTk.PhotoImage(pilImage)
		self.current_image = pilImage	# pilImage.show()
		return image

	def update_image(self):
		if self.win.overrideredirect():
			self.w,self.h = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
			u_image = self.make_image(self.itr, self.op_range_x, self.op_range_y)		# self.canvas = Label(win, width=self.h, height=self.h, image=u_image)
			self.canvas.configure(background='black',image=u_image)						# self.canvas.pack(fill="both", expand="yes")
			self.canvas.image = u_image

		else:
			self.w,self.h = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
			u_image = self.make_image(self.itr, self.op_range_x, self.op_range_y)
			self.canvas.configure(image=u_image)
			self.canvas.image = u_image

	def join_image(self, bgimage):
		area = (int(self.w/2-100), int(self.h/2-100), int(self.w/2+100), int(self.h/2+100))
		bgimage.paste(self.load_icon, area)
		load_image = ImageTk.PhotoImage(bgimage)
		print("inside join_image")
		return load_image 


	def double_click(self, event):	# double click is used for zooming in
		x, y = event.x, event.y    	# temp = self.join_image(self.current_image)
		self.itr += 100				# self.canvas.configure(image=temp)
		self.zoom *= ZOOM_FACTOR			# self.canvas.image = temp
		print("iter: ", self.itr)
		o_x = scale(x,(0, self.w),self.op_range_x)
		o_y = scale(y,(0, self.h),self.op_range_y)
		self.op_range_x = (o_x-self.zoom, o_x+self.zoom)
		self.op_range_y = (o_y-self.zoom, o_y+self.zoom)
		print(f"x: {self.op_range_x}, y: {self.op_range_y}")
		self.steps.append((self.op_range_x, self.op_range_y))
		new_image = self.make_image(itr=self.itr, r_x=self.op_range_x, r_y=self.op_range_y)
		self.canvas.configure(image=new_image)
		self.canvas.image = new_image
		self.num_back = 1
		print(f'x: {event.x}, y: {event.y}')


	def back(self, event): # zoom out to previos step
		if len(self.steps) == 0:
			return

		else:
			if self.num_back == 1:
				self.steps.pop()
			self.zoom /= ZOOM_FACTOR
			step = self.steps.pop()
			self.itr -= 100
			self.op_range_x = step[0]
			self.op_range_y = step[1]
			new_image = self.make_image(itr=self.itr, r_x=self.op_range_x, r_y=self.op_range_y)
			self.canvas.configure(image=new_image)
			self.canvas.image = new_image
			print(f'x: {event.x}, y: {event.y}')
			self.num_back = 0

	def reset_image(self, event):
		self.itr = INIT_ITER
		self.zoom = 1
		self.op_range_x, self.op_range_y = (-2, 1), (-1, 1)
		new_image = self.make_image(itr = self.itr, r_x=self.op_range_x, r_y=self.op_range_y)
		self.canvas.configure(image=new_image)
		self.canvas.image = new_image
		print("image reseted")


def create_window(window):
	def minimize():
		w, h = window.winfo_screenwidth()-100, window.winfo_screenheight()-100
		window.overrideredirect(False)
		window.geometry("%dx%d+0+0" % (w, h))
		window.update()
		window.update_idletasks()
		canvas.update_image()

	def maximize():
		window.overrideredirect(True)
		w, h = window.winfo_screenwidth(), window.winfo_screenheight()
		window.geometry("%dx%d+0+0" % (w, h))
		window.update()
		window.update_idletasks()
		canvas.update_image()

	w, h = window.winfo_screenwidth()-100, window.winfo_screenheight()-100
	window.geometry("%dx%d+0+0" % (w, h))
	window.focus_set()    
	window.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
	window.bind("<f>", lambda e: maximize()) 
	window.bind("<m>", lambda e: minimize())

if __name__ == '__main__':
	root = Tk()
	create_window(root)
	canvas = WindowCanvas(root)
	root.mainloop()
