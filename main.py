import re
from tkinter import *
from tkinter import colorchooser
from tkinter.filedialog import asksaveasfilename
from subprocess import *
from threading import Thread
import os

master = Tk()
master.configure(bg="#121213")
master.geometry("400x800")
master.resizable(False,False)
master.title("MSI PerKeyRgb Creator")
pixel = PhotoImage(width=1, height=1)

output = -1
record = False
currentcolor = "ffffff"
mode = StringVar()
modes = ["Mode: steady"]
mode.set(modes[0])
preview = False
outputtext = []

recordbutton = Button(master,text="Record", font="Arial 20", fg="#ffffff", bg="#282e33", highlightcolor="#95989a", command=lambda:togglerecord())
recordbutton.place(x=0, y=0, relwidth=0.5, height=200, anchor="nw")

Button(master,text="Choose Color", font="Arial 20", fg="#ffffff", bg="#282e33", highlightcolor="#95989a", command=lambda:colorpick()).place(x=200, y=0, relwidth=0.5, height=200, anchor="nw")

drop = OptionMenu(master, mode, *modes)
drop.configure(bg="#282e33", highlightcolor="#95989a", borderwidth=0, fg="#ffffff", font="Arial 15")
drop.place(x=0, y=200, anchor="nw", relwidth=1, height=50)

Button(master, text="Clear Recording", bg="#282e33", highlightcolor="#95989a", borderwidth=0, fg="#ffffff", font="Arial 15", command=lambda:clearoutput()).place(x=0, y=250, relwidth=1, height=50)

outputbox = Text(master, state=DISABLED)
outputbox.place(relwidth=1, height=400, x=0, y=300, anchor="nw")

previewbutton = Button(master, text="Preview: Off", bg="#282e33", highlightcolor="#95989a", borderwidth=0, fg="#ffffff", font="Arial 15", command=lambda:togglepreview())
previewbutton.place(x=0, y=700, relwidth=1, height=50)

Button(master,text="Save and Apply", font="Arial 15", fg="#ffffff", bg="#282e33", highlightcolor="#95989a", command=lambda:export()).place(x=0, y=750, relwidth=1, height=50, anchor="nw")

def keypress():
    global output
    global record
    global mode
    global outputtext
    global drop
    global outputbox
    print(output)
    print(mode.get())
    if record and (output != -1):
        merge = str(output) + " " + str(mode.get()[6:]) + " " + currentcolor
        strloc = False
        for i in range(0,len(outputtext)):
            if str(output) in outputtext[i]:
                strloc = True
                outputtext.pop(i)
                break
        if not strloc:
            outputtext.append(merge)
        print(outputtext)
    outputbox.configure(state=NORMAL)
    outputbox.delete("1.0", "end")
    for i in outputtext:
        outputbox.insert("end", (i + "\n"))
    outputbox.see("end")
    outputbox.configure(state=DISABLED)
    fname = "preview.txt"
    with open(fname, 'w') as fp:
        for line in outputtext:
            fp.write(line + "\n")
    if preview and record:
        os.system("msi-perkeyrgb -m GE75 -d")
        os.system("msi-perkeyrgb -m GE75 -c %s" % (fname))

def togglerecord():
    global recordbutton
    global record
    if record:
        record = False
        recordbutton.configure(activebackground="#ececec", activeforeground="#000000")
    else:
        record = True
        recordbutton.configure(activebackground="#ff5a57", activeforeground="#ffffff")

def colorpick():
    global currentcolor
    getcolor = colorchooser.askcolor(title="Choose color")[1]
    currentcolor = str(getcolor).lower().replace("#", "")
    print (currentcolor)

def disablerec():
    global record
    global recordbutton
    record = False
    recordbutton.configure(bg="#282e33")
    recordbutton.configure(activebackground="#ececec", activeforeground="#000000")

def clearoutput():
    global outputbox
    global outputtext
    print(outputtext)
    outputtext.clear()
    outputbox.configure(state=NORMAL)
    outputbox.delete("1.0", "end")
    outputbox.configure(state=DISABLED)
    if preview:
        fname = "preview.txt"
        with open(fname, 'w') as fp:
            for line in outputtext:
                fp.write(line + "\n")
        os.system("msi-perkeyrgb -m GE75 -d")
        os.system("msi-perkeyrgb -m GE75 -c %s" % (fname))

def export():
    global outputtext
    fname = asksaveasfilename(filetypes=(("Text File", "*.txt"),))
    with open(fname, 'w') as fp:
        for line in outputtext:
            fp.write(line + "\n")
    os.system("msi-perkeyrgb -m GE75 -d")
    os.system("msi-perkeyrgb -m GE75 -c %s"%(fname))

def togglepreview():
    global preview
    global previewbutton
    if preview:
        preview = False
        previewbutton.configure(text="Preview: Off")
        os.system("msi-perkeyrgb -m GE75 -d")
    else:
        preview = True
        previewbutton.configure(text="Preview: On")
        fname = "preview.txt"
        with open(fname, 'w') as fp:
            for line in outputtext:
                fp.write(line + "\n")
        os.system("msi-perkeyrgb -m GE75 -d")
        os.system("msi-perkeyrgb -m GE75 -c %s" % (fname))

if os.path.isfile('preview.txt'):
    with open('preview.txt') as f:
        outputtext = f.read().splitlines()
    outputbox.configure(state=NORMAL)
    outputbox.delete("1.0", "end")
    for i in outputtext:
        outputbox.insert("end", (i + "\n"))
    outputbox.see("end")
    outputbox.configure(state=DISABLED)

windowid = recordbutton.winfo_id()
p = Popen(["xev", "-event", "keyboard", "-1", "-id", str(windowid)], stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)

def readprocess():
    global output
    for line in p.stdout:
        savedline = line.strip("\n")
        loc = savedline.find("keycode")
        if loc > 0:
            output = re.sub("[^0-9]", "", savedline[loc+8:loc+11])

master.bind("<KeyPress>", lambda event:keypress())
recordbutton.bind("<Leave>", lambda event:disablerec())
thread = Thread(target=readprocess)
thread.start()
mainloop()