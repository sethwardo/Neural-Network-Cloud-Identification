'''
Seth Ward
Desc: Allows labeling of cloud images

Usage: python3 cloud-labeling.py 4 3 400 clouds.csv

'''

from tkinter import *
from tkinter import messagebox
import time, sys
import urllib.request
import io
from PIL import Image,ImageTk
import pandas as  pd
import numpy as np

if len(sys.argv) < 5:
    print("cloud-labeling.py <num wide> <num high> <image width px> <in.csv>")
    sys.exit(0)

only_show_non_labeled = True

labels = ['Cirrus','Stratus','Cumulus','Rain','No Clouds','Bad Pic']  # Change me!


    
num_wide = int(sys.argv[1])
num_high = int(sys.argv[2])
image_width = int(sys.argv[3])
infilename = sys.argv[4]

df = pd.read_csv(infilename)



if 'Label' not in df.columns:
	df['Label'] = np.nan


def loadWeatherFile(filename):
  global image_width
  url = "http://uindy-weathercam.s3.us-east-2.amazonaws.com/" + filename
  fh = urllib.request.urlopen(url)
  print(f"Read {url}")
  im = Image.open(io.BytesIO(fh.read()))
  width, height = im.size
  print(width)
  image_height = image_width / width * height
  im = im.resize( (int(image_width), int(image_height)), Image.ANTIALIAS)
  return (image_width, image_height, im)

def wasClicked(event = None):
	if not event:
		return
	global df
	global labels
	index = event.widget.home_index
	df.at[index,'Label'] = event.widget.label_index
	event.widget.label_link.config(text = labels[event.widget.label_index])

def saveAndExit(event = None):
	global df 
	global infilename
	global master
	df.to_csv(infilename)
	messagebox.showinfo(message=f"{infilename} saved.")
	master.destroy()


def displayImage(index, df, m, x, y, memory, labels):
	dx = 5 # Allow up to 5 buttoons per image
	dy = 3 # Two rows per image/button
	#filename = it[index]
	print(index, x, y)
	filename = df.iloc[index]['Cloud File']
	f = Frame(m)
	(width, height, im) = loadWeatherFile(filename)
	canvas = Canvas(f, width = width, height = height)
	img = ImageTk.PhotoImage(im)
	memory.append(img) # The create image doesn't imbed img's reference, so gets destroyed, keep it in a list so it displays
	canvas.create_image(0, 0, anchor=NW, image=img) 
	canvas.pack(side="left", fill="both", expand=True)
	f.grid(column = x * dx, row = y * dy, columnspan=dx)

	if np.isnan(df.iloc[index]['Label']):
		label = Label(m, text = "not set")
	else:
		label = Label(m, text = labels[ int(df.iloc[index]['Label']) ]  )
	label.grid(column = x * dx + 1, row = y * dy + 1)

	for i in range(len(labels)):
		button = Button(m, text=labels[i])
		button.home_index = index
		button.label_link = label
		button.label_index = i
		button.grid(column = x * dx + i, row = y * dy + 2)
		button.bind('<Button>', wasClicked)
	


master = Tk()
memory = []

# Do some filtering based on which images need labeling
index_list = df.index
if only_show_non_labeled:
	index_list = []
	for i in range(len(df.index)):
		if np.isnan(df.at[i,'Label']):
			index_list.append(i)


mini = min(num_high * num_wide, len(index_list))
for i in range(mini):
	displayImage(index_list[i], df, master, int(i % num_wide), int(i / num_wide) + 1, memory, labels)

button = Button(master, text="Save and Exit")
button.grid(column = 0, row = 0)
button.bind('<Button>', saveAndExit)




master.mainloop()
