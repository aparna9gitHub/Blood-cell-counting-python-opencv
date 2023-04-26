from tkinter import *
import ctypes,os
from PIL import ImageTk, Image
import tkinter.messagebox as tkMessageBox
from tkinter.filedialog import askopenfilename
import cv2
import time
from utils import iou
from scipy import spatial
from darkflow.net.build import TFNet

options = {'model': 'cfg/tiny-yolo-voc-3c.cfg',
           'load': 3750,
           'threshold': 0.1,
           'gpu': 0.7}

tfnet = TFNet(options)

pred_bb = []  # predicted bounding box
pred_cls = []  # predicted class
pred_conf = []  # predicted class confidence

def blood_cell_count(file_name):
    rbc = 0
    wbc = 0
    platelets = 0

    cell = []
    cls = []
    conf = []

    record = []
    tl_ = []
    br_ = []
    iou_ = []
    iou_value = 0

    tic = time.time()
    image = cv2.imread(file_name)
    image = cv2.resize(image,(640,480))
    output = tfnet.return_predict(image)

    for prediction in output:
        label = prediction['label']
        confidence = prediction['confidence']
        tl = (prediction['topleft']['x'], prediction['topleft']['y'])
        br = (prediction['bottomright']['x'], prediction['bottomright']['y'])
        if label == 'RBC' and confidence < .5:
            continue
        if label == 'WBC' and confidence < .25:
            continue
        if label == 'Platelets' and confidence < .25:
            continue
        # clearing up overlapped same platelets
        if label == 'Platelets':
            if record:
                tree = spatial.cKDTree(record)
                index = tree.query(tl)[1]
                iou_value = iou(tl + br, tl_[index] + br_[index])
                iou_.append(iou_value)
            if iou_value > 0.1:
                continue
            record.append(tl)
            tl_.append(tl)
            br_.append(br)
        center_x = int((tl[0] + br[0]) / 2)
        center_y = int((tl[1] + br[1]) / 2)
        center = (center_x, center_y)
        if label == 'RBC':
            color = (255, 0, 0)
            rbc = rbc + 1
        if label == 'WBC':
            color = (0, 255, 0)
            wbc = wbc + 1
        if label == 'Platelets':
            color = (0, 0, 255)
            platelets = platelets + 1
        radius = int((br[0] - tl[0]) / 2)
        image = cv2.circle(image, center, radius, color, 2)
        font = cv2.FONT_HERSHEY_COMPLEX
        image = cv2.putText(image, label, (center_x - 15, center_y + 5), font, .5, color, 1)
        cell.append([tl[0], tl[1], br[0], br[1]])
        if label == 'RBC':
            cls.append(0)
        if label == 'WBC':
            cls.append(1)
        if label == 'Platelets':
            cls.append(2)
        conf.append(confidence)
    toc = time.time()
    pred_bb.append(cell)
    pred_cls.append(cls)
    pred_conf.append(conf)
    avg_time = (toc - tic) * 1000
    cv2.imwrite('temp.png', image)
    return [rbc,wbc,platelets]


        
main = Tk()
main.title("Blood Cell Counting")
main.geometry("940x570")
main.config(bg="#FFC6F2")
Label(main,text="RBC,WBC and platelet Counting using Image Processing",font=("",18,"bold"),bg="#FFC6F2",fg="black").place(x=140,y=20)
can = Canvas(main,width=250,height=450,bg="#8D87B1",relief="solid",bd=1,highlightthickness=0)
can.place(x=30,y=80)
Label(main,text="Menu",font=("",12,"bold"),bg="#8D87B1",fg="black").place(x=44,y=70)
can2 = Canvas(main,width=280,height=100,bg="#8D87B1",relief="solid",bd=1,highlightthickness=0)
can2.place(x=435,y=400)
Label(main,text="COUNTING RESULT",font=("",12,"bold"),bg="#8D87B1",fg="black").place(x=495,y=385)
txtbx = Text(main,width=23,height=3,font=("",14,"bold"),relief="solid",bd=0,highlightthickness=0)
txtbx.place(x=449,y=418)

def browse():
    global val
    try:
        can3.destroy()
    except:
        pass
    try:
        can4.destroy()
    except:
        pass
    can3 = Canvas(main,width=280,height=180,relief="solid",bd=0,highlightthickness=0)
    can3.place(x=320,y=115)

    can4 = Canvas(main,width=280,height=180,relief="solid",bd=0,highlightthickness=0)
    can4.place(x=620,y=115)
    file = askopenfilename(initialdir=os.getcwd(), title="Select Image", filetypes=( ("images", ".png"),("images", ".jpg"),("images", ".jpeg")))
    if file!='' or file!= None:
        img= ImageTk.PhotoImage(Image.open(file).resize((280,180)))
        imgl = Label(can3,image=img)
        imgl.pack()
        imgl.photo=img
        val = blood_cell_count(file)
        img= ImageTk.PhotoImage(Image.open('temp.png').resize((280,180)))
        img2 = Label(can4,image=img)
        img2.pack()
        img2.photo=img
        t = "RBC = ?\nWBC = ?\nPlatelet = ?"
        txtbx.delete(1.0, "end-1c")
        txtbx.insert("end-1c",t)

def RBC():
    global val
    try:
        t = txtbx.get(1.0, 'end-1c').split('\n')
        t2 = "RBC = "+str(val[0])
        t = t2+"\n"+t[1]+"\n"+t[2]
        txtbx.delete(1.0, "end-1c")
        txtbx.insert("end-1c",t)
    except:
        pass
def WBC():
    global val
    try:
        t = txtbx.get(1.0, 'end-1c').split('\n')
        t2 = "WBC = "+str(val[1])
        t = t[0]+"\n"+t2+"\n"+t[2]
        txtbx.delete(1.0, "end-1c")
        txtbx.insert("end-1c",t)
    except:
        pass
def Platelets():
    global val
    try:
        t = txtbx.get(1.0, 'end-1c').split('\n')
        t2 = "Platelet = "+str(val[2])
        t = t[0]+"\n"+t[1]+"\n"+t2
        txtbx.delete(1.0, "end-1c")
        txtbx.insert("end-1c",t)
    except:
        pass
def reset():
        t = "RBC = ?\nWBC = ?\nPlatelet = ?"
        txtbx.delete(1.0, 'end-1c')
        txtbx.insert("end-1c",t)
def Exit():
    global main
    result = tkMessageBox.askquestion(
        'Blood Cell Counting', 'Are you sure you want to exit?', icon="warning")
    if result == 'yes':
        main.destroy()
        exit()
    else:
        tkMessageBox.showinfo(
            'Return', 'You will now return to the main screen')
        
Button(main,text="Browse Input",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=browse,relief="solid",bd=2,highlightthickness=0).place(x=50,y=110)
Button(main,text="Count RBC",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=RBC,relief="solid",bd=2,highlightthickness=0).place(x=50,y=160)
Button(main,text="Count WBC",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=WBC,relief="solid",bd=2,highlightthickness=0).place(x=50,y=210)
Button(main,text="Count Platelet",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=Platelets,relief="solid",bd=2,highlightthickness=0).place(x=50,y=260)
Button(main,text="Reset",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=reset,relief="solid",bd=2,highlightthickness=0).place(x=50,y=310)
Button(main,text="Exit",font=("",12,"bold"),width=20,height=1,bg="#EAF2D7",fg="black",command=Exit,relief="solid",bd=2,highlightthickness=0).place(x=50,y=360)
txt = """Project By:
Name- Aparna Bharti
Reg no- 38220207"""
Label(main,text=txt,font=('',14,"bold"),bg="#8D87B1",fg="black").place(x=55,y=415)

can3 = Canvas(main,width=280,height=180,relief="solid",bd=0,highlightthickness=0)
can3.place(x=320,y=115)

can4 = Canvas(main,width=280,height=180,relief="solid",bd=0,highlightthickness=0)
can4.place(x=620,y=115)

Label(main,text="Input Image",font=("",12,""),bg="#FFC6F2",fg="black").place(x=420,y=300)

Label(main,text="Output Image",font=("",12,""),bg="#FFC6F2",fg="black").place(x=720,y=300)


main.mainloop()
