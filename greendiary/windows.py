import tkinter as tk
import tkinter.filedialog as filedialog


import winsound



# Get file name through tkinter
def getFile(initialDir, windowTitle='Undefined', filetype='xlsx'):
    root = tk.Tk()
    root.withdraw()
    filename = ''
    if filetype == 'xlsx':
        filename =  filedialog.askopenfilename(initialdir = initialDir,title=windowTitle,filetypes=(('excel file','*.xlsx'),))
    elif filetype == 'csv':
        filename =  filedialog.askopenfilename(initialdir = initialDir,title=windowTitle,filetypes=(('csv file','*.csv'),))
    elif filetype == 'all':
        filename =  filedialog.askopenfilename(initialdir = initialDir,title=windowTitle,filetypes=(('all files','*.*'),))
    print (filename)
    return filename



# Get directory name through tkinter
def getDirectoryName():
	root = tk.Tk()
	root.withdraw()
	directoryName = filedialog.askdirectory()	
	print(directoryName)
	return directoryName




# Get file save as name
def getFileSaveAs(initialDir, windowTitle='Undefined', filetype='xlsx'):
	root = tk.Tk()
	root.withdraw()
	filename = ''
	if filetype == 'xlsx':
		filename =  filedialog.asksaveasfilename(initialdir = initialDir,title=windowTitle,filetypes=(('excel file','*.xlsx'),))
	elif filetype == 'csv':
		filename =  filedialog.asksaveasfilename(initialdir = initialDir,title=windowTitle,filetypes=(('csv file','*.csv'),))
	elif filetype == 'all':
		filename =  filedialog.asksaveasfilename(initialdir = initialDir,title=windowTitle,filetypes=(('all files','*.*'),))	
	print (filename)
	return filename





'''
def getInputThroughGUI(input_label='Password', button_label='Enter', hide_actual_characters=True):
    class GetEntry():
        def __init__(self, master, input_label, button_label, hide_actual_characters):
            self.master = master
            self.label = tk.Label(master, text=input_label)
            self.label.grid(column=0, row=0)
            self.entry_contents = None
            if hide_actual_characters:
                self.entry = tk.Entry(master, width=100, show='*')
            else:
                self.entry = tk.Entry(master, width=100)
            self.entry.grid(row=0, column=1)
            self.entry.focus_set()
            tk.Button(master, text=button_label, width=10, command=self.callback).grid(row=10,column=0)
        def callback(self):
            self.entry_contents = self.entry.get()
            self.master.destroy()
    master = tk.Tk()
    master.title("Input Data")
    master.geometry('350x200')
    GE = GetEntry(master, input_label, button_label, hide_actual_characters)
    master.mainloop()
    return GE.entry_contents
'''

'''
def getInputThroughGUI(input_label='Password', button_label='Enter', hide_actual_characters=True):
    class GetEntry():
        def __init__(self, input_label, button_label, hide_actual_characters):
            self.master = tk.Tk()
            self.master.title("Input Data")
            self.master.geometry('350x200')
            self.label = tk.Label(self.master, text=input_label)
            self.label.grid(column=0, row=0)
            self.entry_contents = None
            if hide_actual_characters:
                self.entry = tk.Entry(self.master, width=100, show='*')
            else:
                self.entry = tk.Entry(self.master, width=100)
            self.entry.grid(row=0, column=1)
            self.entry.focus_set()
            tk.Button(self.master, text=button_label, width=10, command=self.callback).grid(row=10,column=0)
        def callback(self):
            self.entry_contents = self.entry.get()
            self.master.destroy()
    GE = GetEntry(input_label, button_label, hide_actual_characters)
    GE.master.mainloop()
    return GE.entry_contents
'''



def makeSound():
    winsound.Beep(440, 2000)

