
import numpy as np
from numpy.core.fromnumeric import size
from psychopy.visual import text
import pylab as plt
from datetime import datetime
import psychopy 
from psychopy import visual
from psychopy import core
from psychopy import event
from psychopy import gui
from psychopy import sound
import os.path
import glob
import time
from pyo import *
import pyo
import serial



# port.readData
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
Center = [0,0]
BaseTime=[0.8,1,1.2,1.5]
CueTime=[1] #Test
ResponseTime=[2] #official
Timing=[BaseTime,CueTime,ResponseTime]

now=datetime.now()
now="-".join([str(now.day),str(now.month),str(now.year)])

# Assign values to the participant
Exp=True
folder_path = os.path.dirname(os.path.abspath(__file__))
print(folder_path)
Respath= os.path.join(folder_path,'Results')
ExperimentType='1'

# folder_path = "C:\\Users\\lora.fanda\\Documents\\GROWN\\"
SoundFile= os.path.join(folder_path,'auditory_naming','*.wav')
ImageFiles= os.path.join(folder_path,'picture_naming','*.png')
reading_list = open(os.path.join(folder_path,'reading_completion','reading_comp.txt')).read().split('\n')

image_list = []
sound_list = []
for filename in glob.glob(ImageFiles): #assuming gif
    image_list.append(filename)
for filename in glob.glob(SoundFile): #assuming gif
    sound_list.append(filename)

print('¦...... Folder Used is:  ', folder_path)
print('¦............ Number of Images:  ', np.size(image_list))
print('¦............ Number of Sounds:  ', np.size(sound_list))

def onetrial(mywin,Stim,fix,Timing,FileName,TrialNumber,BlockNumber,isImage=False,isText=False,isSound = False):

    # Exit=onetrial(mywin,s,fix,Timing,FileName,n+1)
    quitnow=False
    tic=time.time()
    event.clearEvents(eventType=None)
    if isSound==True: Sound = sound.Sound(Stim) 
    if isText==False:
        BlockName = Stim.split('\\')[-2]
        StimNameTemp = Stim.split('\\')[-1][0:-4]
        StimNumber, StimName = StimNameTemp.split('_')
    else:
        BlockName = 'reading_completion'
        StimNumber, StimSentence, StimName = Stim.split('_')
    # 0: Define time durations base, cue and response
    np.random.shuffle(Timing[0])
    BaseTime= Timing[0][0]
    CueTime=Timing[1][0]
    ResponseTime=Timing[2][0]
    
    ## 1: BASELINE
    # #Show Fix
    fix.draw()
    # tic=time.time()
    mywin.flip()

    el1=time.time()-tic
    core.wait(BaseTime-el1)
    print('¦--- baseline duration: '+ str(time.time()-tic)[0:7] + '   right: '+ str(BaseTime))

    ## 2: CUE
    # IntroFile= os.path.join(folder_path, folder_path,'instructionscreen.png') 
    tic=time.time()

    circle = visual.Circle(
        pos= [-880,460],
        win=mywin,
        units="pix",
        radius=80,
        fillColor=[-1, -1, -1],
        lineColor=[-1, -1, -1]
    )


    if isImage: # if image
        StimVisual=visual.SimpleImageStim(win=mywin,image=Stim)
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'a')
    elif isText:
        StimVisual=visual.TextStim(win=mywin,text="",color='black',height=50)
        StimVisual.setText(text=StimSentence)
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'c')
        core.wait(3.5)
    else:
        StimVisual=visual.SimpleImageStim(win=mywin,image=os.path.join(folder_path,'listen_icon.png'))
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'b')
        Sound.play()
        core.wait(Sound.getDuration()+1)     
    el2=time.time()-tic
    core.wait(CueTime-el2)
    print('¦--- cue duration:      '+  str(time.time()-tic)[0:7]+ '   right: '+ str(CueTime))

    ## 3: RESPONSE
    tic=time.time()
    ResponseText=visual.TextStim(win=mywin,text="",color='black',height=100)
    ResponseText.setText(text='?')
    ResponseText.draw()
    # circle = visual.Circle(
    #     pos= [900,-500],
    #     win=mywin,
    #     units="pix",
    #     radius=200,
    #     fillColor=[0,0,0],
    #     lineColor=[0,0,0]
    # )
    # circle.draw()
    mywin.flip()
    # port.write(b'1')
    

    while True:
        if len(event.getKeys(keyList='space'))>0:
            # port.write(b'v')
            ReactionTime=time.time()-tic
            ValidTrial = 1
            break        
        if len(event.getKeys(keyList='x'))>0:
            # port.write(b'x')
            ReactionTime = time.time()-tic
            ValidTrial = 0 
            break
        if len(event.getKeys(keyList='n'))>0:
            ReactionTime = 0
            ValidTrial = 0 
            quitnow=True
            break
        if len(event.getKeys(keyList='q'))>0:
            Exp=False
            break
    # circle = visual.Circle(
    #     pos= [900,-500],
    #     win=mywin,
    #     units="pix",
    #     radius=200,
    #     fillColor=[0,0,0],
    #     lineColor=[0,0,0]
    # )
    # circle.draw()
    print('¦--- response duration: '+  str(time.time()-tic)[0:7])
    # Get response time
    Resp=[ValidTrial,ReactionTime]
    print('¦----- ReactionTime: '+str(ReactionTime)[0:7])

    with open(FileName,"a") as FileData:
        ####################change on#####################################
        txt=[str(TrialNumber),str(BlockNumber),str(BlockName),StimNumber,StimName,str(Resp[0]),str(Resp[1]) ]
        #####################change off ####################################
        txt=[str(t) for t in txt]
        FileData.write(",".join(txt))
        FileData.write('\n')

    return quitnow


while True:
    DlgInit = gui.Dlg(title="Functional Language Mapping Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Age:")
    DlgInit.addField('Sex:', choices=["M", "F"])
    DlgInit.addField('handedness:', choices=["R", "L"])
    DlgInit.addField("Volume (0-1): ",0.5)
    DlgInit.addField('COM port','COM9')
    DlgInit.show()
    InitialData = DlgInit.data
    if InitialData==['', '', 'M', 'R', 0.5,'COM9']:# Cancel if press
        Exp=False
        break
    else:
        SbjNumber=InitialData[0]
        Age=InitialData[1]
        Sex=InitialData[2]
        Handedness=InitialData[3]
        Volume=InitialData[4]
        com_port = InitialData[5]
        FileName=SbjNumber+'_FLM_'+now+'.txt'
        FileName=os.path.join(Respath,FileName)
        print(FileName)
        if os.path.isfile(FileName):
            DlgFile = gui.wx.MessageDialog(None,"File exist. Do you want to continue or define other parameters(yes) or overwrite file(no)",style=gui.wx.YES|gui.wx.NO|gui.wx.ICON_QUESTION)
            Resp=DlgFile.ShowModal()
            if Resp == 5103:
                with open(FileName,'w') as FileData:
                    FileData.write('\n')
                    FileData.write('SubjectNumber : '+SbjNumber+'\n')
                    FileData.write('Sex : '+Sex+'\n')
                    FileData.write('Age : '+Age+'\n')
                    FileData.write('Handedness : '+Handedness+'\n')
                    FileData.write('TrialNumber,BlockNumber,BlockName,StimNumber,StimName,ResponseAccuracy,ResponseTime')
                    FileData.write('\n')
                break
        else:
            with open(FileName,'w') as FileData:
                FileData.write('SubjectNumber : '+SbjNumber+'\n')
                FileData.write('Sex : '+Sex+'\n')
                FileData.write('Age : '+Age+'\n')
                FileData.write('Handedness : '+Handedness+'\n')
                ######################change on #################################
                FileData.write('TrialNumber,BlockNumber,BlockName,StimNumber,StimName,ResponseAccuracy,ResponseTime')
                ######################change off#################################
                FileData.write('\n')
            break
if Exp:
        # add input for the com port 
        if WithTriggers == 'Yes':
            port = serial.Serial(com_port,9600, timeout=5) 
            port.readData

        
        mywin=visual.Window([1800,1000], pos=[0,0], monitor="default",waitBlanking=True,units="pix",color='white',fullscr=True,allowGUI=True)
        mywin.logOnFlip(msg='Flipped',level=1)
        fix=visual.TextStim(win=mywin,text="+",pos=[0,0], color='black',height=30)
        repeatNum=1 # how many repetitions of each item

        # 1.1 show intro image
        IntroFile= os.path.join(folder_path,'instructionscreen.png')
        Intro=visual.SimpleImageStim(win=mywin,image=IntroFile)
        Intro.draw()
        mywin.flip()
        # 1.2 Press SPACE key to continue
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break

        # 2.1 Picture Naming Block
        Exit=False
        IntroText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        IntroText.setText(text='Picture Naming:\nName the picture when the question mark appears. Letàs start with 3 Training examples.\n\nPress x for bad trial.\nPress space to continue\nPress n to skip the block.\nPress q to quit')
        IntroText.draw()
        mywin.flip()
        #2.2 Press SPACE key to continue
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break
        # 2.3 TRAINING
        CountText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        Count=[3,2,1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)
        np.random.shuffle(image_list)
        for i,s in enumerate(image_list):
            if Exit or i==3: break
            print('\nTrial '+str(i+1)+'¦ Block Training')
            Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=True)
            # Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=True,save=False)
        ResponseText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        ResponseText.setText(text='Training has ended. \nPress space to continue')
        ResponseText.draw()     
        mywin.flip()   
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break

        # 2.3 Countdown
        CountText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        Count=[3,2,1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)
        # 2.4 PICTURE naming: Loops for repeatNum times 
        Exit=False
        for n in range(repeatNum):
            #shuffle image order shown
            np.random.shuffle(image_list)
            for i,s in enumerate(image_list):
                if i >50: Exit=True
                if Exit: break
                print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
                Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isImage=True)
        ResponseText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        ResponseText.setText(text='Picture Naming has ended. \nPress space to continue')
        ResponseText.draw()     
        mywin.flip()       
        while True: 
            if len(event.getKeys(keyList='space'))>0: break

        # 3.1 AUDIO Naming Block
        Exit=False
        IntroText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        IntroText.setText(text='Auditory Naming:\n Respond with the word that best explains the sentence when the question mark appears. We will start with 3 Training examples. \n\nPress x for bad trial.\nPress space to continue\nPress n to skip the block.\nPress q to quit')
        IntroText.draw()
        mywin.flip()
        #3.2 Press SPACE key to continue
        while True: 
            if len(event.getKeys(keyList='space'))>0: break


        # 3.3 AUDIO naming: Loops for repeatNum times
        for n in range(repeatNum):
            #shuffle image order shown
            np.random.shuffle(sound_list)
            for i,s in enumerate(sound_list):
                if Exit or i == 3: break
                print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
                Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isSound=True)
        ResponseText=visual.TextStim(win=mywin,text="",color=[0,0,0])
        ResponseText.setText(text='Training has ended. \nPress space to continue')
        ResponseText.draw()     
        mywin.flip()   
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break

        # Countdown
        CountText=visual.TextStim(win=mywin,text="",color='black')
        Count=[3,2,1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)

        # 3.3 AUDIO naming: Loops for repeatNum times
        for n in range(repeatNum):
            #shuffle image order shown
            np.random.shuffle(sound_list)
            for i,s in enumerate(sound_list):
                if Exit: break
                print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
                Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isSound=True)
        ResponseText=visual.TextStim(win=mywin,text="",color='black')
        ResponseText.setText(text='Auditory Naming has ended. \nPress space to continue')
        ResponseText.draw()     
        mywin.flip()       
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break
        core.wait(1)


        # 5.1 READING repetition Block
        Exit=False
        IntroText=visual.TextStim(win=mywin,text="",color='black')
        IntroText.setText(text='Reading Sentence Completion:\nRead quietly and complete the sentence vocally to the best of your ability\n\nPress x for bad trial.\nPress space to continue\nPress n to skip the block.\nPress q to quit')
        IntroText.draw()
        mywin.flip()
        #5.2 Press SPACE key to continue
        while True:
            if len(event.getKeys(keyList='space'))>0:
                break

        # 5.3 TRAINING READING repetition: Loops for repeatNum times
        for n in range(repeatNum):
            #shuffle image order shown
            np.random.shuffle(reading_list)
            for i,s in enumerate(reading_list):
                if Exit or i == 3: break
                print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
                Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isText=True)
        # Countdown        
        CountText=visual.TextStim(win=mywin,text="",color='black')
        Count=[3,2,1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)
        # 5.2 READING repetition: Loops for repeatNum times
        for n in range(repeatNum):
            #shuffle image order shown
            np.random.shuffle(reading_list)
            for i,s in enumerate(reading_list):
                if Exit: break
                print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
                Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isText=True)
        ResponseText=visual.TextStim(win=mywin,text="",color='black')
        ResponseText.setText(text='Word Repetition has ended.\n\nPress space to continue')
        ResponseText.draw()     
        mywin.flip()       
        while True:
                if len(event.getKeys(keyList='space'))>0:
                    break

        ResponseText=visual.TextStim(win=mywin,text="",color='black',height=50)
        ResponseText.setText(text='Congrats!!!! You are done!!!\n\nPress space to end the experiment')
        ResponseText.draw()     
        mywin.flip()       
        while True:
                if len(event.getKeys(keyList='space'))>0:
                    break
