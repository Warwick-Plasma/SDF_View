#!/usr/bin/env python

#No try/catch on importing sys. If this doesnt work then you've got bigger problems
import sys
import math
#Test for numpy
try:
    import numpy
except:
    print("Unable to import numpy. Please install it")
    exit()
#Test for matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
except:
	print("Unable to import matplotlib. Please install it")
#Test for sdf
try:
    import sdf_helper as sh
    import sdf_derived as sd
    import sdf
except:
    print("Unable to import the SDF reader modules. Please build these first")
    exit()
#Test for tkinter
try:
    import tkFileDialog
    from Tkinter import *
except:
    print("Unable to import the necessary parts of tkinter. Please install the TK library and the tkinter Python module")
    exit()
#Test for skimage, but dont fail if it isnt available
try:
    from skimage import measure
except:
    print("Unable to import scikit-image (skimage) module. This is needed for 3D visualisation")

class sdfview():

    listbox = None
    current_data = None
    plotwindow = None
    fig = None
    win = None
    
    def abs_sqr_button(self) :
        base=self.current_data[self.listbox.get(ANCHOR)]
        dv=sd.abs_sq(base)
        self.current_data[dv.name]=dv
        self.populate_listbox(self.current_data)


    def average_button(self) :
        base=self.current_data[self.listbox.get(ANCHOR)]
        dv=sd.average(base,direction=1)
        self.current_data[dv.name]=dv
        self.populate_listbox(self.current_data)


    def quit_button(self) :
        self.win.destroy()
        return

    def load_button(self) :
        fname=tkFileDialog.askopenfilename(defaultextension=".sdf",filetypes=[('SDF file','*.sdf'),('All files','*.*')])
        if (fname is None) :
            return
        self.fig.clear()
        self.load_datafile(fname)

    def draw_button(self) :
        data=self.current_data[self.listbox.get(ANCHOR)]
        self.fig.clear()
        self.plotwindow = self.fig.add_subplot(111)
        if(len(data.dims) == 1) :
            sh.plot1d(data, figure=self.fig, subplot=self.plotwindow)
        if(len(data.dims) == 2) :
            sh.plot2d(data, figure=self.fig, subplot=self.plotwindow)
        self.fig.subplots_adjust(bottom=0.2)
        self.fig.canvas.draw()

    def build_pack_button(self, parent,**kwargs) :
        b=Button(parent,kwargs)
        b.pack(expand=0)
        return b

    def build_gui(self) :
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
        from matplotlib.figure import Figure

        #Create the window
        self.win=Tk()
        self.win.title("SDF Viewer")
        self.win.geometry('800x500')

        #Create the panel splitting the window left/right
        left_right=PanedWindow(self.win)
        left_right.pack(fill=BOTH, expand=1)
        #Create the listbox and add it to the left right split
        self.listbox = Listbox(left_right)
        left_right.add(self.listbox)

        #Create the panel splitting the window vertically
        top_bottom = PanedWindow(left_right, orient=VERTICAL)
        left_right.add(top_bottom)

        #Create the panel which will contain the buttons
        top=PanedWindow(top_bottom, orient=HORIZONTAL)
        top_bottom.add(top)

        #Add the buttons
        top.add(self.build_pack_button(top,text="Open File",command=self.load_button,anchor=NW))
        top.add(self.build_pack_button(top,text="Draw Figure", command=self.draw_button,anchor=NW))
        top.add(self.build_pack_button(top,text="Quit",command=self.quit_button,anchor=NW))
        top.add(self.build_pack_button(top,text="Abs Square",command=self.abs_sqr_button,anchor=NW))
        top.add(self.build_pack_button(top,text="Average",command=self.average_button,anchor=NW))        
        top.add(Label(top,text="SDF Viewer Version 0.1"))

        #Create the figure object and adjust the borders because matplot lib doesnt 
        #do a good job by default
        self.fig = Figure()
        self.fig.subplots_adjust(bottom=0.4)

        #Get the reference to the canvas object and add it to the tk objects
        canvas = FigureCanvasTkAgg(self.fig, master=top_bottom)
        canvas._tkcanvas.pack(side=BOTTOM,expand=1)
        top_bottom.add(canvas.get_tk_widget())

        toolbar = NavigationToolbar2TkAgg(canvas,top_bottom)
        toolbar.update()
        canvas.show()

    def populate_listbox(self,keylist) :
        self.listbox.delete(0,END)
        for key,value in keylist.iteritems():
            self.listbox.insert(END,(value.name))

    def get_valid_keys(self,data) :
        keylist={}
        for key, value in data.__dict__.iteritems():
            if (type(value) == sdf.BlockPlainVariable and \
                hasattr(value,'grid')): keylist[value.name]=value
        return keylist

    def load_datafile(self,filename) :
        full_data = sh.getdata(filename,verbose=False)
        self.current_data = self.get_valid_keys(full_data)
        self.populate_listbox(self.current_data)
        return self.current_data

    def import_data(self,full_data) :
        self.current_data=self.get_valid_keys(full_data)
        self.populate_listbox(self.current_data)
        return self.current_data

    def __init__(self,alpha=None) : 
        self.build_gui()
        if (alpha is not None) :
            if(type(alpha) == sdf.BlockList) :
                self.import_data(alpha)
            else :
                self.load_datafile(alpha)
        mainloop()

if __name__ == '__main__' :
    if (len(sys.argv) > 1) :
        dobj=sdfview(sys.argv[1])
    else :
        dobj=sdfview()
