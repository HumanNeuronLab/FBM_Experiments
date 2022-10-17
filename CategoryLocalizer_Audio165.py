
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
import serial
from pyo import *

###   Detials CHANGE TEXT FILE NAMES
# Define the hardcoded values
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
Center = [0,0]
BaseTime=[0.2,0.3,0.4,0.5]
# CueTime=[0.8,1,1.2,1.5]
CueTime=[2] # doesnt matter, the sounds are only 2s long
# Center = [0,0] #Test
# BaseTime=[1.2,1.3,1.4,1.5] #Test
# CueTime=[1.8,2,2.2,2.5] #Test
ResponseTime=[2] #official
Timing=[BaseTime,CueTime,ResponseTime]
now=datetime.now()
now="-".join([str(now.day),str(now.month),str(now.year)])
Exp=True
folder_path = os.path.dirname(os.path.abspath(__file__))
Respath= os.path.join(folder_path,'Results')

AudioFiles= os.path.join(folder_path,'AudCatLoc_natsounds165','wav','*.wav')
CategFile= os.path.join(folder_path,'AudCatLoc_natsounds165','category_labels.csv')
print(AudioFiles)
new_audio_list = []
for filename in glob.glob(AudioFiles): #assuming gif
    new_audio_list.append(filename)

new_audio_list.sort()
audio_list = []
for i in range(0,len(new_audio_list),165):
    audio_list.append(random.sample(new_audio_list[i:i+165],k=165))
audio_list = [item for sublist in audio_list for item in sublist]# Display relevant information
print('¦...... Folder Used is:  ', folder_path)
print('¦............ Number of Sounds:  ', np.size(audio_list))

# Open Categories from Excel
from csv import DictReader
with open(CategFile, 'r') as read_obj:
    # pass the file object to DictReader() to get the DictReader object
    dict_reader = DictReader(read_obj,)
    # get a list of dictionaries from dct_reader
    list_of_dict = list(dict_reader)
    # print list of dict i.e. rows
    # print(list_of_dict(1))

# function ONETRIAL
def onetrial(mywin,Stim,fix,Timing,FileName,TrialNumber,BlockNumber,isImage=False,isRepeatImage=False, timeOfRepeat = 0,start_tic=0):

    circle = visual.Circle(
        pos= [-900,480],
        win=mywin,
        units="pix",
        radius=60,
        fillColor=[-1, -1, -1],
        lineColor=[-1, -1, -1]
    )

    circle_gray = visual.Circle(
        pos= [-900,480],
        win=mywin,
        units="pix",
        radius=60,
        fillColor=[0, 0, 0],
        lineColor=[0, 0, 0]
    )    
    
    quitnow=False
    tic=time.time()
    # event.clearEvents(eventType=None)
    BlockName = 'CatLocAudio165'
    Stim1 = Stim.split('\\')[-1]
    Stim1 = Stim1.split('.')[0]
    print(Stim1)
    StimName, StimNumber = Stim1.split('_')[0:2]
    Sound = sound.Sound(Stim) 
    
    # 0: Define time durations base, cue and response
    np.random.shuffle(Timing[0])
    BaseTime= Timing[0][0]
    CueTime=Timing[1][0] # Cue is always only the first value
    ResponseTime=Timing[2][0]
    
    ## 1: BASELINE
    circle_gray.draw()
    fix.draw()
    mywin.flip()
    el1=time.time()-tic
    core.wait(BaseTime-el1)
    print('¦--- Baseline (fix) duration: '+ str(time.time()-tic)[0:7] + '   right: '+ str(BaseTime))

    ## 2: CUE
    tic=time.time()
    onset_tic = tic - start_tic
    if isImage: # if image
        StimVisual=visual.SimpleImageStim(win=mywin,image=Stim)
        StimVisual.draw()
        circle.draw()
        mywin.flip()        
        core.wait(0.01)
        StimVisual.draw()
        circle_gray.draw()
        mywin.flip()
        # core.wait()
        if WithTriggers == 'Yes':
            port.write(b'v')
        print("¦--- Showing:                ", Stim1, '   Repeat:',isRepeatImage)
    else:
        StimVisual=visual.SimpleImageStim(win=mywin,image=os.path.join(folder_path,'audio_icon.png'))
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        core.wait(0.05)
        StimVisual.draw()
        circle_gray.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'b')
        Sound.play()
        core.wait(Sound.getDuration())     
    el2=time.time()-tic
    core.wait(CueTime-el2)
    print('¦--- cue duration:      '+  str(time.time()-tic)[0:7]+ '   right: '+ str(CueTime))

    ReactionTime = 0
    ValidTrial = 0 
    if isRepeatImage:
        timeOfRepeat = time.time()
        if WithTriggers == 'Yes':
            port.write(b'a')
    else:
        timeOfRepeat = 0

    el2=time.time()-tic
    core.wait(CueTime-el2)
    duration = time.time()-tic
    sample_offset=str(time.time()+duration)
    print('¦--- Cue (Image) duration:    '+  str(duration)[0:7]+ '   right: '+ str(CueTime))

    ## 3: RESPONSE
    tic=time.time()
    mywin.flip()

    if len(event.getKeys(keyList='q'))>0:
        quitnow = True


    # Save to txt file
    if len(event.getKeys(keyList='space'))>0:
        duration = time.time()-tic
        ReactionTime = time.time()
        sample_offset=str(time.time()+duration)
        if WithTriggers == 'Yes':
            port.write(b'b')
            port.write(b'b')

    if (ReactionTime == 0 and timeOfRepeat == 0) or (ReactionTime != 0 and timeOfRepeat != 0):
        ValidTrial=1

    if timeOfRepeat !=0:
        trial_type="go"
        if ReactionTime == 0:
            response_type = "miss"
        else: 
            response_type = "hit"
    else:
        trial_type="no_go"
        if ReactionTime == 0:
            response_type="correct_rejection"
        else: 
            response_type = "false_alarm"


    Resp=[ValidTrial,ReactionTime]
    with open(FileName,"a") as FileData:
        ####################change on#####################################
        # 'onset,duration,trial_type,category,exemplar,response_type,response_time'
        txt=[str(onset_tic),str(duration)[0:7],trial_type,BlockName,StimNumber,response_type,str(Resp[1])]
        # CategoryLocalizer,63,word,1664293981.9973466,0,0
        # txt=[str(BlockName),StimNumber,StimName,str(timeOfRepeat),str(Resp[0]),str(Resp[1])]
        #####################change off ####################################
        txt=[str(t) for t in txt]
        FileData.write("\t".join(txt))
        FileData.write('\n')

    return quitnow, timeOfRepeat, ReactionTime

# SETUP THE START-UP GUI
while True:
    DlgInit = gui.Dlg(title="Category Localizer (Audio165) Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Volume (0-1): ",1)
    DlgInit.addField("PORT (COM): ",'COM3')
    DlgInit.addField("Use serial triggers?: ",choices= ["No","Yes"])
    DlgInit.show()
    InitialData = DlgInit.data
    if DlgInit.OK: # InitialData==['', '', 'M', 'R', 1,'COM9','No']:# Cancel if press
        SbjNumber=InitialData[0]
        Volume=InitialData[1]
        PortName=InitialData[2]
        WithTriggers=InitialData[3]
        FileName='sub-'+SbjNumber+'_task-LocalizerAud165_events.tsv'
        FileName=os.path.join(Respath,FileName)
        print(FileName)
        if os.path.isfile(FileName):
            DlgFile = gui.wx.MessageDialog(None,"File exist. Do you want to continue or define other parameters(yes) or overwrite file(no)",style=gui.wx.YES|gui.wx.NO|gui.wx.ICON_QUESTION)
            Resp=DlgFile.ShowModal()
            if Resp == 5103:
                with open(FileName,'w') as FileData:
                    FileData.write('\n')
                    FileData.write('sub- : '+SbjNumber+'\n')
                    FileData.write('task- : LocalizerAud165\n')
                    # txt=[str(BlockName),StimNumber,StimName,str(timeOfRepeat),str(Resp[0]),str(Resp[1])]
                    FileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time')
                    FileData.write('\n')
                break
        else:
            with open(FileName,'w') as FileData:
                FileData.write('SubjectNumber : '+SbjNumber+'\n')
                ######################change on #################################
                FileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time')
                ######################change off#################################
                FileData.write('\n')
            break
    else:
        Exp=False
        break

# START THE EXPERIMENT
if Exp:
    if WithTriggers == 'Yes':
        port = serial.Serial(PortName,9600, timeout=5) #COM4 is the right one
        port.readData

    # 0. SETUP WINDOW PROPERTIES
    mywin=visual.Window([1100,1100], pos=[0,0], monitor="default",waitBlanking=True,units="pix",color='white',fullscr=True,allowGUI=True)
    fix=visual.TextStim(win=mywin,text="+",pos=[0,0], color='black',height=30)
    repeatNum=1 # how many repetitions of each item

    # 1. INTRODUCTION
    Exit=False
    IntroText=visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Category Localizer Audio 165:\n\n Press SPACE BAR when you see a repeating sound. \n\nPress q to quit')
    IntroText.draw()
    mywin.flip()
    #Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0: break

    # 2. EXPERIMENT
    CountText=visual.TextStim(win=mywin,text="",color='black')
    Count=[3,2,1]
    for i in Count:
        CountText.setText(text=i)
        CountText.draw()
        mywin.flip()
        core.wait(1)
    
    #  Insert the random image repetition
    np.random.shuffle(audio_list)
    repeatIndex = [False for i in range(len(audio_list))]
    new_i=random.randrange(5,16)
    old_audio_list = audio_list
    for i,item in enumerate(old_audio_list):
        if i <new_i:
            continue
        rand_index = random.randrange(5,16)
        print(i, new_i, rand_index)
        print(' ')
        audio_list.insert(i,audio_list[i-1])
        repeatIndex.insert(i,True)
        new_i=i+rand_index
    onset=time.time()
    timeOfRepeat=0
    ReactTime=0
    start_tic=time.time()

    for i,s in enumerate(audio_list):
        if Exit or len(event.getKeys(keyList='q'))>0: break
        print('\nTrial '+str(i+1)+'¦ ')
        Exit,timeOfRepeat, ReactTime=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=False, isRepeatImage=repeatIndex[i],timeOfRepeat=timeOfRepeat,start_tic=start_tic)
        print(timeOfRepeat,ReactTime)
        # Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=True,save=False)

    # 3. END OF TASK
    ResponseText=visual.TextStim(win=mywin,text="",color='black',height=20)
    ResponseText.setText(text='Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n...'+ FileName[-50:-1])
    ResponseText.draw()     
    mywin.flip()       
    while True:
            if len(event.getKeys(keyList='space'))>0:
                break