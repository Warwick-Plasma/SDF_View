#!/usr/bin/env python

listbox = None
current_data = None
plotwindow = None
fig = None

def quit_button() :
	exit()
	return

def load_button() :
	fname=tkFileDialog.askopenfilename(defaultextension=".sdf",filetypes=[('SDF file','*.sdf'),('All files','*.*')])
	if (fname is None) :
		return
	fig.clear()
	load_datafile(fname)
	return

def draw_button() :
	data=current_data[listbox.get(ANCHOR)]
	global plotwindow
	global fig
	fig.clear()
        a = fig.add_subplot(111)
        plotwindow = a
	if(len(data.dims) == 1) :
		draw_1d(data)
	if(len(data.dims) == 2) :
		draw_2d(data)
	fig.canvas.draw()
	return

def draw_1d(data) : 
	if(data.dims[0] == data.grid.dims[0]) :
		grid=data.grid
	else :
		grid=data.grid_mid
        plotwindow.plot(grid.data[0],data.data)
	plotwindow.set_xlabel('x('+grid.units[0]+')')
	plotwindow.set_ylabel(data.name.split("/")[1].strip() + '(' + data.units + ')')
	return

def draw_2d(data) :
	import numpy 
        if(data.dims[0] == data.grid.dims[0]) :
                gridx=data.grid
        else :
                gridx=data.grid_mid
        if(data.dims[1] == data.grid.dims[1]) :
                gridy=data.grid
        else :
                gridy=data.grid_mid

        plotwindow.set_xlabel('x('+gridx.units[0]+')')
        plotwindow.set_ylabel('y('+gridy.units[1]+')')

	zmin=numpy.amin(data.data)
	zmax=numpy.amax(data.data)
	pc=plotwindow.pcolorfast(gridx.data[1],gridy.data[0],data.data.transpose(),vmin=zmin,vmax=zmax)
	
	cb=plotwindow.figure.colorbar(pc,ticks=numpy.linspace(zmin,zmax,num=10).tolist())
	cb.set_label((data.name.split("/")[1].strip() + '(' + data.units + ')'))
	return

def build_gui() :

	import matplotlib

	from numpy import arange, sin, pi
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

	from matplotlib.figure import Figure

	win=Tk()
	win.title("SDF Viewer")
	win.geometry('800x500')
	m1=PanedWindow(win,name='m1')
	m1.pack(fill=BOTH, expand=1)

	left = Listbox(m1)
	m1.add(left)

	m2 = PanedWindow(m1, orient=VERTICAL)
	m1.add(m2)

	top=PanedWindow(m2, orient=HORIZONTAL)
	m2.add(top)
	top.add(Button(top,text="Open File",command=load_button))
	top.add(Button(top,text="Draw Figure", command=draw_button))
	top.add(Button(top,text="Quit",command=quit_button,anchor=E))
	top.add(Label(top,text="SDF Viewer Version 0.1"))

	global fig
	fig = Figure(figsize=(1, 1), dpi=100)
	fig.subplots_adjust(bottom=0.20,left=0.20)

	canvas = FigureCanvasTkAgg(fig, master=m2)
	toolbar = NavigationToolbar2TkAgg(canvas,m2)
	toolbar.update()
	canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
	canvas.show()
	m2.add(canvas.get_tk_widget())
        
	global listbox
	listbox=left
	return

def populate_listbox(keylist) :
	global listbox
	listbox.delete(0,END)
        for key,value in keylist.iteritems():
                listbox.insert(END,(value.name))
	return

def get_valid_keys(data) :
	keylist={}

	for key, value in data.__dict__.iteritems():
        	if (type(value) == sdf.BlockPlainVariable and hasattr(value,'grid')): keylist[value.name]=value
	return keylist

def load_datafile(filename) :
	global current_data
	full_data = sh.getdata(filename)
	current_data = get_valid_keys(full_data)
	populate_listbox(current_data)
	return current_data

import sdf_helper as sh
import sdf
import tkFileDialog
from Tkinter import *

build_gui()
mainloop()
