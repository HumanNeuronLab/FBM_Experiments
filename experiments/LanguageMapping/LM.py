"""
MIT License

Copyright (c) 2026 Lora Fanda
See LICENSE file in the project root for full license information.
"""
import os
import glob
import time
import codecs
import numpy as np
import serial
import psychopy
from datetime import datetime
import psychtoolbox as ptb

# Set preferences
psychopy.prefs.hardware['audioLib'] = ['sounddevice','PTB','pyo', 'pygame']
from psychopy import visual, core, event, gui, sound

Center = [0,0]
BaseTime=[1.1,1.2,1.3,1.4]
CueTime=[1] # Official
ResponseTime=[2] # Official

Timing=[BaseTime,CueTime,ResponseTime]
now=datetime.now()
timestamp = str(now.hour)+'h'+str(now.minute)+'m'+str(now.second)+'s'
now="-".join([str(now.day),str(now.month),str(now.year)])

Exp=True
folder_path = os.path.dirname(os.path.abspath(__file__))
Respath= os.path.join(folder_path,'Results')
ExperimentType='1'
# choose_experiment = ['Picture Naming','Auditory Definition','Sentence Completion']

choose_language=[]
'''
# Define global constants and variables
CENTER = [0, 0]
BASE_TIME = [1.1, 1.2, 1.3, 1.4]
CUE_TIME = [1]
RESPONSE_TIME = [2]
TIMING = [BASE_TIME, CUE_TIME, RESPONSE_TIME]
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
RES_PATH = os.path.join(FOLDER_PATH, 'Results')
CHOOSE_EXPERIMENT = ['Picture Naming', 'Auditory Definition', 'Sentence Completion', 'Motor Tasks']
CHOOSE_LANGUAGE = [filename[-3:] for filename in glob.glob(os.path.join(FOLDER_PATH, 'auditory_*'))]
'''

for filename in glob.glob(os.path.join(folder_path,'auditory_*')): #assuming gif
    choose_language.append(filename[-3:])

def onetrial(mywin,Stim,fix,Timing,FileName,TrialNumber,BlockNumber,isImage=False,isText=False,isSound=False):
    # Exit=onetrial(mywin,s,fix,Timing,FileName,n+1)

    quitnow=False
    tic=time.time()
    event.clearEvents(eventType=None)
    # if isSound==True: Sound = sound.Sound(Stim) 
    if isSound==True: Sound = sound_cache[Stim]    
    if isText==False:
        BlockName = os.path.basename(os.path.dirname(Stim))
        StimNameTemp = os.path.splitext(os.path.basename(Stim))[0]
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
    # circle_gray.draw()
    fix.draw()
    mywin.flip()
    el1=time.time()-tic
    core.wait(BaseTime-el1)
    print('¦--- Baseline (fix) duration: '+ str(time.time()-tic)[0:7] + '   right: '+ str(BaseTime))

    ## 2: CUE
    tic=time.time()
    onset_tic = tic - start_tic
    mywin.frameIntervals = []
    mywin.recordFrameIntervals = True
    if isImage: # if image
        # StimVisual=visual.SimpleImageStim(win=mywin,image=Stim)
        StimVisual = image_cache[Stim]
        StimVisual.draw()
        rectangle.draw()
        mywin.callOnFlip(port.write, bytes(bytearray([1]))) if WithTriggers == 'Yes' else None
        mywin.flip()
        core.wait(1)

    elif isText:
        # StimVisual=visual.TextStim(win=mywin,text="",color='black',height=50)
        # StimVisual.setText(text=StimSentence)
        StimVisual = text_cache[Stim]
        StimVisual.draw()
        rectangle.draw()
        mywin.callOnFlip(port.write, bytes(bytearray([3]))) if WithTriggers == 'Yes' else None
        mywin.flip()
        if Selected_language=="GER":
            CueTime=5.5
            core.wait(5.5)
        elif Selected_language=="FRE" or Selected_language=="ITA": 
            CueTime=4.0
            core.wait(4.0)
        else:
            CueTime=3.5
            core.wait(3.5)
    else:
        fix.draw() 
        rectangle.draw()
        mywin.callOnFlip(port.write, bytes(bytearray([2]))) if WithTriggers == 'Yes' else None
        next_flip = mywin.getFutureFlipTime(clock='ptb')
        Sound.play(when=next_flip)        
        mywin.flip()
        CueTime =Sound.getDuration()
        core.wait(Sound.getDuration())  
    el2=time.time()-tic
    core.wait(CueTime-el2)
    duration = time.time()-tic
    mywin.recordFrameIntervals = False
    print('¦--- Cue (stim) duration:    '+  str(duration)[0:7]+ '   right: '+ str(CueTime))

    ## 3: RESPONSE
    tic=time.time()
    ResponseText=visual.TextStim(win=mywin,text="",color='black',height=40)
    ResponseText.setText(text='?')
    ResponseText.draw()
    mywin.callOnFlip(port.write, bytes(bytearray([10]))) if WithTriggers == 'Yes' else None
    mywin.flip()

    if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
        quitnow = True
    
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0 or len(event.getKeys(keyList='103'))>0: #CORRECT
            [trial_type,response_type,ReactionTime,duration,ValidTrial]=['go',"correct",time.time()-tic,time.time(),1]
            break        
        if len(event.getKeys(keyList='x'))>0 or len(event.getKeys(keyList='num_6'))>0: #WRONG ANSWER
            [trial_type,response_type,ReactionTime,duration,ValidTrial]=['go',"wrong",time.time()-tic,time.time(),0]
            break
        if len(event.getKeys(keyList='n'))>0 or len(event.getKeys(keyList='num_8'))>0: #NEXT BLOCK
            [trial_type,response_type,ReactionTime,duration,ValidTrial,quitnow] = ["go","wrong", 0,0, 0,True]
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0: #QUIT EXPERIMENT
            [trial_type,response_type,ReactionTime,duration,ValidTrial,Exp,quitnow] = ["go","wrong",0,0,0 ,False,True]
            break
        
        duration = time.time()-tic
        ReactionTime = time.time()

    Resp=[ValidTrial,ReactionTime]
    print('¦----- ReactionTime: '+str(ReactionTime)[0:7])

    with open(FileName,"a") as FileData:
        ####################change on#####################################
        # 'onset,duration,trial_type,category,exemplar,response_type,response_time'
        txt=[str(onset_tic)[0:10],str(duration)[0:7],trial_type,BlockName,StimNumber,response_type,str(Resp[1])]
        # CategoryLocalizer,63,word,1664293981.9973466,0,0
        # txt=[str(BlockName),StimNumber,StimName,str(timeOfRepeat),str(Resp[0]),str(Resp[1])]
        #####################change off ####################################
        txt=[str(t) for t in txt]
        FileData.write("\t".join(txt))
        FileData.write('\n')
    return quitnow


while True:
    DlgInit = gui.Dlg(title="Functional Brain Mapping Initialisation")    
    DlgInit.addText("Subject Info", color="Green")
    DlgInit.addField("Subject ID:")
    DlgInit.addText("Experiment Settings", color="red")
    DlgInit.addField("Volume (0-1): ",1)
    DlgInit.addField("PORT (COMX): ",'COM3')
    DlgInit.addField("Use serial triggers?: ",choices= ["No","Yes"])
    DlgInit.addField("Choose language: ",choices= choose_language)
    DlgInit.addField("Choose screen: ",choices= [0,1,2])
    DlgInit.addField("Display resolution: ",choices= [[1920,1080],[1800,800],[1280,1024]])
    DlgInit.show()
    InitialData = DlgInit.data
    if DlgInit.OK: # InitialData==['', '', 'M', 'R', 1,'COM9','No']:# Cancel if press
        SbjNumber = InitialData[0]
        Volume = InitialData[1]
        PortName = InitialData[2]
        WithTriggers = InitialData[3]
        Selected_language = InitialData[4]
        # Selected_experiment = InitialData[5]
        choice_screen = InitialData[5]
        FileName='sub-'+SbjNumber+'_task-LanguageMapping_datetime-'+ now +'('+timestamp+')_language-'+Selected_language+'_events.tsv'
        print(FileName)
        FileName=os.path.join(Respath,FileName)
        disp_size = InitialData[6]
        if os.path.isfile(FileName):
            DlgFile = gui.wx.MessageDialog(None,"File exist. Do you want to continue or define other parameters(yes) or overwrite file(no)",style=gui.wx.YES|gui.wx.NO|gui.wx.ICON_QUESTION)
            Resp = DlgFile.ShowModal()

            if Resp == gui.wx.ID_YES:
                # continue
                pass
            elif Resp == gui.wx.ID_NO:
                # overwrite
                with open(FileName, 'w') as FileData:
                    FileData.write('SubjectNumber : ' + SbjNumber + '\n')
                    FileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time\n')
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
    # reading_list = open(os.path.join(folder_path,'reading_completion_'+Selected_language,'reading_completion_'+Selected_language+'.txt'),encoding='utf-8')
    # # reading_list = codecs.open(os.path.join(folder_path,'reading_completion_'+Selected_language,'reading_comp_'+Selected_language+'.txt'),encoding='utf-8')
    # reading_list = reading_list.read().split('\n')
    # # reading_list = open(os.path.join(folder_path,'reading_completion_'+Selected_language,'reading_comp_'+Selected_language+'.txt')).read().split('\n')
    # print(choose_language)

    # image_list = []
    # sound_list = []
    # for filename in glob.glob(ImageFiles): #assuming gif
    #     image_list.append(filename)
    # for filename in glob.glob(SoundFile): #assuming gif
    #     sound_list.append(filename)

    reading_list = open(os.path.join(folder_path, 'reading_completion_' + Selected_language,'reading_completion_' + Selected_language + '.txt'), encoding='utf-8')
    reading_list = reading_list.read().split('\n')
    print(choose_language)

    image_list = []
    sound_list = []
    for filename in glob.glob(ImageFiles):
        image_list.append(filename)
    for filename in glob.glob(SoundFile):
        sound_list.append(filename)


    print('¦...... Folder Used is:  ', folder_path)
    print('¦............ Number of Images:  ', np.size(image_list))
    print('¦............ Number of Sounds:  ', np.size(sound_list))

    if WithTriggers == 'Yes':
        port = serial.Serial(PortName,9600, timeout=5) #COM4 is the right one

    # 0. Initialize the window
    mywin = visual.Window(disp_size, pos=[0,0], monitor="default",screen=choice_screen,waitBlanking=True,units="pix",color='white',fullscr=True,allowGUI=True)
    mywin.recordFrameIntervals = False
    mywin.frameIntervals = []

    # PRELOAD STIMULI
    image_cache = {fname: visual.SimpleImageStim(win=mywin, image=fname) for fname in image_list}
    sound_cache = {fname: sound.Sound(fname) for fname in sound_list}

    text_cache = {}
    for stim in reading_list:
        if stim.strip() == "":
            continue
        StimNumber, StimSentence, StimName = stim.split('_')
        text_cache[stim] = visual.TextStim(win=mywin, text=StimSentence, color='black', height=50)

    # circle_gray = visual.Circle(pos= [-900,480],win=mywin,units="pix",radius=60,fillColor=[0, 0, 0],lineColor=[0, 0, 0]) 
    # circle = visual.Circle(pos= [-900,480],win=mywin,units="pix",radius=60,fillColor=[-1, -1, -1],lineColor=[-1, -1, -1]) 
    # rectangle_gray = visual.Rect(win=mywin,width=70*4,height=140*4,fillColor="black",lineColor="black",pos=[-1 * disp_size[0] / 2 + 50 / 2,disp_size[1] / 2 - 100 / 2],units="pix")
    rectangle = visual.Rect(
        win=mywin,
        width=70,
        height=140,
        fillColor="black",
        lineColor="black",
        pos=[-1 * disp_size[0] / 2 + 50 / 2, disp_size[1] / 2 - 100 / 2],
        units="pix",
    )    

    fix = visual.TextStim(win=mywin,text="+",pos=[0,0], color='black',height=30)
    repeatNum = 1 # how many repetitions of each item

    # 1.1 show intro image
    IntroFile = os.path.join(folder_path,'instructionscreen.png')
    Intro = visual.SimpleImageStim(win=mywin,image=IntroFile)
    # circle_gray.draw()
    Intro.draw()
    mywin.flip()
    # 1.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

    # 2.1 Picture Naming Block
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Picture Naming:\nName the picture when the question mark appears. Lets start with 3 Training examples.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
    # circle_gray.draw()
    IntroText.draw()
    mywin.flip()

    #2.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

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
        # circle_gray.draw()
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
    # circle_gray.draw()
    mywin.flip()   
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

    # 2.3 Countdown
    CountText = visual.TextStim(win=mywin,text="",color='black')
    Count = [3,2,1]
    for i in Count:
        CountText.setText(text=i)
        CountText.draw()
        # circle_gray.draw()
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
    # circle_gray.draw()     
    mywin.flip()       
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

    # 3.1 AUDIO Naming Block
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Auditory Naming: \nRespond with the word that best explains the sentence when the question mark appears. We will start with 3 Training examples. \n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
    IntroText.draw()
    # circle_gray.draw()
    mywin.flip()
    #3.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

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
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

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
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()
    core.wait(1)

    # 5.1 READING repetition Block
    Exit = False
    IntroText = visual.TextStim(win=mywin,text="",color='black')
    IntroText.setText(text='Reading Sentence Completion (Verify Keyboard Language before beginning):\nRead quietly and complete the sentence vocally to the best of your ability. \n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit')
    IntroText.draw()
    mywin.flip()
    #5.2 Press SPACE key to continue
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4'))>0:
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

    # 5.3 TRAINING READING repetition: Loops for repeatNum times
    for n in range(repeatNum):
        #TODO: shuffle image order shown only once
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
        # shuffle word order shown
        np.random.shuffle(reading_list)
        for i,s in enumerate(reading_list):
            if Exit: break
            print('\nTrial '+str(i+1)+'¦ Block '+str(n+1))
            Exit=onetrial(mywin,s,fix,Timing,FileName,i+1,n+1,isText=True)
    ResponseText = visual.TextStim(win=mywin,text="",color='black')
    ResponseText.setText(text='Word Repetition has ended.\n\nPress SPACE BAR to continue')
    ResponseText.draw()     
    mywin.flip()       
    while True:
        if len(event.getKeys(keyList='space'))>0 or len(event.getKeys(keyList='num_4')):
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()

    # 3. END OF TASK
    ResponseText = visual.TextStim(win=mywin,text="",color='black',height=20)
    ResponseText.setText(text='Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n...'+ FileName[-70:-1])
    ResponseText.draw()     
    mywin.flip()       
    while True:
        if len(event.getKeys(keyList='space'))>0 or  len(event.getKeys(keyList='num_4')):
            break
        if len(event.getKeys(keyList='q'))>0 or len(event.getKeys(keyList='num_9'))>0:
            exit()
