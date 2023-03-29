
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

###   Detials

## TODO: Change folder infromation 
# DONE
## TODO: Change automatically the language of the task (Or Select? Dropdown menu)
# DONE
## TODO: Option to change the window: Select current or extended window 


# Define the hardcoded values
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
Center = [0,0]
BaseTime=[0.8,1,1.2,1.5]
CueTime=[1] # Official
ResponseTime=[2] # Official
Timing=[BaseTime,CueTime,ResponseTime]
now=datetime.now()
timestamp = str(now.hour)+'h'+str(now.minute)+'m'+str(now.second)+'s'
now="-".join([str(now.day),str(now.month),str(now.year)])
Exp=True
folder_path = os.path.dirname(os.path.abspath(__file__))
print(folder_path)
Respath= os.path.join(folder_path,'Results')
ExperimentType='1'

choose_language=[]
for filename in glob.glob(os.path.join(folder_path,'auditory_*')): #assuming gif
    choose_language.append(filename[-3:])

def onetrial(mywin,Stim,fix,Timing,FileName,TrialNumber,BlockNumber,isImage=False,isText=False,isSound = False):
    # Exit=onetrial(mywin,s,fix,Timing,FileName,n+1)
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
        if WithTriggers == 'Yes': port.write(b'a')
    elif isText:
        StimVisual=visual.TextStim(win=mywin,text="",color='black',height=50)
        StimVisual.setText(text=StimSentence)
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        core.wait(0.05)
        StimVisual.draw()
        circle_gray.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'c')
        core.wait(3.5)
    else:
        StimVisual=visual.SimpleImageStim(win=mywin,image=os.path.join(folder_path,'listen_icon.png'))
        StimVisual.draw()
        circle.draw()
        mywin.flip()
        core.wait(0.05) 
        StimVisual.draw()
        circle_gray.draw()
        mywin.flip()
        if WithTriggers == 'Yes': port.write(b'b')
        Sound.play()
        core.wait(Sound.getDuration()+1)  # TODO why plus one   
    el2=time.time()-tic
    core.wait(CueTime-el2)
    duration = time.time()-tic
    sample_offset=str(time.time()+duration)
    print('¦--- Cue (Image) duration:    '+  str(duration)[0:7]+ '   right: '+ str(CueTime))

    ## 3: RESPONSE
    tic=time.time()
    ResponseText=visual.TextStim(win=mywin,text="",color='black',height=100)
    ResponseText.setText(text='?')
    ResponseText.draw()
    mywin.flip()
    core.wait(0.05)
    ResponseText.draw()
    circle_gray.draw()
    mywin.flip()
    if WithTriggers == 'Yes': port.write(b'1')
    if len(event.getKeys(keyList='q'))>0:
        quitnow = True
    
    while True:

        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='100'))>0 or len(event.getKeys(keyList='103'))>0: #CORRECT
            if WithTriggers == 'Yes': port.write(b'v') 
            trial_type = "go"
            response_type = "correct"
            duration = time.time()-tic
            ReactionTime = time.time()
            ValidTrial = 1
            break        
        if len(event.getKeys(keyList='x'))>0 or len(event.getKeys(keyList='102'))>0: #WRONG ANSWER
            trial_type = "go"
            response_type = "wrong"
            duration = time.time()-tic
            ReactionTime = time.time()
            if WithTriggers == 'Yes': port.write(b'x')
            ValidTrial = 0 
            break
        if len(event.getKeys(keyList='n'))>0 or len(event.getKeys(keyList='104'))>0: #NEXT BLOCK
            trial_type = "go"
            response_type = "wrong"
            ReactionTime = 0
            duration = 0
            ValidTrial = 0 
            quitnow = True
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='105'))>0: #QUICK EXPERIMENT
            Exp = False
            break
        
        duration = time.time()-tic
        ReactionTime = time.time()
        sample_offset = str(time.time()+duration)
        if WithTriggers == 'Yes':
            port.write(b'b')


    Resp=[ValidTrial,ReactionTime]
    print('¦----- ReactionTime: '+str(ReactionTime)[0:7])

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

    return quitnow


while True:
    DlgInit = gui.Dlg(title="Functional Language Mapping Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Volume (0-1): ",1)
    DlgInit.addField("PORT (COM): ",'COM3')
    DlgInit.addField("Use serial triggers?: ",choices= ["No","Yes"])
    DlgInit.addField("Choose language: ",choices= choose_language)
    DlgInit.addField("Choose screen: ",choices= [0,1,2])
    DlgInit.show()
    InitialData = DlgInit.data
    if DlgInit.OK: # InitialData==['', '', 'M', 'R', 1,'COM9','No']:# Cancel if press
        SbjNumber = InitialData[0]
        Volume = InitialData[1]
        PortName = InitialData[2]
        WithTriggers = InitialData[3]
        Selected_language = InitialData[4]
        choice_screen = InitialData[5]
        FileName='sub-'+SbjNumber+'_task-LanguageMapping_timestamp-'+ now +'('+timestamp+')_lang-'+Selected_language+'_events.tsv'
        print(FileName)
        FileName=os.path.join(Respath,FileName)
        print(FileName)
        if os.path.isfile(FileName):
            DlgFile = gui.wx.MessageDialog(None,"File exist. Do you want to continue or define other parameters(yes) or overwrite file(no)",style=gui.wx.YES|gui.wx.NO|gui.wx.ICON_QUESTION)
            Resp=DlgFile.ShowModal()
            if Resp == 5103:
                with open(FileName,'w') as FileData:
                    FileData.write('\n')
                    FileData.write('sub- : '+SbjNumber+'\n')
                    FileData.write('task- : LanguageMapping\n')
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

    # Add file paths
    SoundFile= os.path.join(folder_path,'auditory_naming_'+Selected_language,'*.wav')
    ImageFiles= os.path.join(folder_path,'picture_naming','*.png')
    reading_list = open(os.path.join(folder_path,'reading_completion_'+Selected_language,'reading_comp_'+Selected_language+'.txt')).read().split('\n')
    print(choose_language)

    image_list = []
    sound_list = []
    for filename in glob.glob(ImageFiles): #assuming gif
        image_list.append(filename)
    for filename in glob.glob(SoundFile): #assuming gif
        sound_list.append(filename)

    print('¦...... Folder Used is:  ', folder_path)
    print('¦............ Number of Images:  ', np.size(image_list))
    print('¦............ Number of Sounds:  ', np.size(sound_list))

    if WithTriggers == 'Yes':
        port = serial.Serial(PortName,9600, timeout=5) #COM4 is the right one
        port.readData

    # 0. Initialize the window
    mywin = visual.Window([1800,1000], pos=[0,0], monitor="default",screen=choice_screen,waitBlanking=True,units="pix",color='white',fullscr=True,allowGUI=True)
    circle_gray = visual.Circle(pos= [-900,480],win=mywin,units="pix",radius=60,fillColor=[0, 0, 0],lineColor=[0, 0, 0]) 
    fix = visual.TextStim(win=mywin,text="+",pos=[0,0], color='black',height=30)
    repeatNum = 1 # how many repetitions of each item

    # 1.1 show intro image
    IntroFile = os.path.join(folder_path,'instructionscreen.png')
    Intro = visual.SimpleImageStim(win=mywin,image=IntroFile)
    circle_gray.draw()
    Intro.draw()
    mywin.flip()
    # 1.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0:
            break

    # 2.1 Picture Naming Block
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Picture Naming:\nName the picture when the question mark appears. Lets start with 3 Training examples.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
    circle_gray.draw()
    IntroText.draw()
    mywin.flip()



    #2.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0:
            break
    start_tic = time.time()
    onset = time.time()
    timeOfRepeat = 0
    ReactTime = 0

    # 2.3 TRAINING
    CountText = visual.TextStim(win=mywin,text="",color='black')
    Count = [3,2,1]
    for i in Count:
        CountText.setText(text=i)
        CountText.draw()
        circle_gray.draw()
        mywin.flip()
        core.wait(1)
    np.random.shuffle(image_list)
    for i,s in enumerate(image_list):
        if Exit or i==3: break
        print('\nTrial '+str(i+1)+'¦ Block Training')
        Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=True)
        # Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,0,isImage=True,save=False)
    ResponseText = visual.TextStim(win=mywin,text="",color='black')
    ResponseText.setText(text='Training has ended. \nPress space to continue')
    ResponseText.draw()   
    circle_gray.draw()
    mywin.flip()   
    while True:
        if len(event.getKeys(keyList='space'))>0:
            break

    # 2.3 Countdown
    CountText = visual.TextStim(win=mywin,text="",color='black')
    Count = [3,2,1]
    for i in Count:
        CountText.setText(text=i)
        CountText.draw()
        circle_gray.draw()
        mywin.flip()
        core.wait(1)

    # 2.4 PICTURE naming: Loops for repeatNum times 
    Exit = False
    for n in range(repeatNum):
        #shuffle image order shown
        np.random.shuffle(image_list)
        for i,s in enumerate(image_list):
            if i>50: Exit=True
            if Exit: break
            print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
            Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isImage=True)
    ResponseText=visual.TextStim(win=mywin,text="",color='black')
    ResponseText.setText(text='Picture Naming has ended. \nPress space to continue')
    ResponseText.draw()
    circle_gray.draw()     
    mywin.flip()       
    while True: 
        if len(event.getKeys(keyList='space'))>0: break

    # 3.1 AUDIO Naming Block
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Auditory Naming: \nRespond with the word that best explains the sentence when the question mark appears. We will start with 3 Training examples. \n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
    IntroText.draw()
    circle_gray.draw()
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
            Exit = onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isSound=True)
    ResponseText = visual.TextStim(win=mywin,text="",color='black')
    ResponseText.setText(text='Training has ended. \nPress space to continue')
    ResponseText.draw()     
    mywin.flip()   
    while True:
        if len(event.getKeys(keyList='space'))>0:
            break

    # Countdown
    CountText = visual.TextStim(win=mywin,text="",color='black')
    Count = [3,2,1]
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
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Reading Sentence Completion (Verify Keyboard Language before beginning):\nRead quietly and complete the sentence vocally to the best of your ability. \n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
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
    CountText = visual.TextStim(win=mywin,text="",color='black')
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
    ResponseText = visual.TextStim(win=mywin,text="",color='black')
    ResponseText.setText(text='Word Repetition has ended.\n\nPress space to continue')
    ResponseText.draw()     
    mywin.flip()       
    while True:
            if len(event.getKeys(keyList='space'))>0:
                break

    # 3. END OF TASK
    ResponseText = visual.TextStim(win=mywin,text="",color='black',height=20)
    ResponseText.setText(text='Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n...'+ FileName[-50:-1])
    ResponseText.draw()     
    mywin.flip()       
    while True:
            if len(event.getKeys(keyList='space'))>0:
                break