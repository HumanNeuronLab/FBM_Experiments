# conda create -n hnlEnv python=3.7
# conda activate hnlEnv
# conda install wxPython
# pip3 install -r requirements.txt
# 
# sudo rmmod lp
# chmod a+rw /dev/parport0
#  

from pyo import *
from os import path
from glob import glob
from time import time
from numpy import random
from psychopy import core
from psychopy import event
from psychopy import gui
from psychopy import parallel
from psychopy import prefs
from psychopy import sound
from psychopy import visual

# Hardcoded values
prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
folderPath = path.dirname(path.abspath(__file__))
resultsPath = path.join(folderPath,'Results')
instructionsFile = path.join(folderPath, 'instructionscreen.png')
pportInt = int("00000101", 2)  # pins 2 and 4 high

baseTime = [1.3] # BaseLine is 0.8, plus 500 ms of sound 
preStimTime = 0.5 # Sound trigger for stims appears 500ms before stimulus
preStimDuration = 0.2
cueTime = [6] #officially 1
responseTime = [2]
timing = [baseTime, cueTime, responseTime]
doExperiment = True
repeatNum = 1
stimuliTypes=['All','Image','Sound','Text']

def countdown(window):
    countText = visual.TextStim(win=window, text="", color=[0,0,0])
    for t in [3, 2, 1]:
        countText.setText(text=t)
        countText.draw()
        window.flip()
        core.wait(1)

def write_data(filename, onset_tic, duration, trialType, blockName, stimNumber, response_type, reactionTime):
    print('¦----- reactionTime: ' + str(reactionTime)[0:7])

    with open(filename,"a") as fileData:
        txt = [str(onset_tic), str(duration)[0:7], trialType, blockName, stimNumber, response_type, str(reactionTime)]
        txt = [str(t) for t in txt]
        fileData.write("\t".join(txt))
        fileData.write('\n')

def task_block(window, fix, circles, stimuliType, introText, itemList, start_tic, filename, pport):
    visual.TextStim(win=window, text=introText, color='black').draw()
    window.flip()

    event.waitKeys(keyList='space')  
    countdown(window)

    stopExp = False
    stopBlock = False
    for n in range(repeatNum):
        random.shuffle(itemList)
        for i, item in enumerate(itemList):
            print('\nTrial ' + str(i+1) + '¦ Block ' + str(n+1))
            stopExp, stopBlock = one_trial(window, fix, circles, stimuliType, item, start_tic, filename, pport)
            if stopBlock: break
    visual.TextStim(win=window, text='Task has ended.\n\nPress space to continue', color='black').draw()     
    window.flip()

    event.waitKeys(keyList='space')

    return stopExp

def one_trial(window, fix, circles, stimuliType, item, start_tic, filename, pport):
    # return [stopExp, stopBlock]
    tic = time()
    event.clearEvents()

    if stimuliType == 'Image':
        blockName = path.basename(path.dirname(item))
        tmp = path.splitext(path.basename(item))[0]
        stimNumber, stimName = tmp.split('_')
    elif stimuliType == 'Sound':
        blockName = 'sound'
        tmp = path.splitext(path.basename(item))[0]
        stimNumber, stimName = tmp.split('_')
        Sound = sound.Sound(item) 
    elif stimuliType == 'Text':
        blockName = 'reading_completion'
        stimNumber, stimSentence, stimName = item.split('_')
    else: 
        return [False, True]

    random.shuffle(timing[0])
    baseTime = timing[0][0]
    cueTime = timing[1][0]
    
    ## BASELINE
    circles[1].draw()
    fix.draw()
    window.flip()
    el1 = time()-tic
    core.wait(baseTime-el1-preStimTime)
    sound.Sound('A', preStimDuration).play()
    core.wait(preStimTime)
    print('¦--- Baseline (fix) duration: ' + str(time()-tic)[0:7] + '   right: ' + str(baseTime))

    ## CUE
    tic = time()
    onset_tic = tic - start_tic
    if stimuliType == 'Image':
        stimVisual = visual.SimpleImageStim(win=window, image=item)
        stimVisual.draw()
        circles[0].draw()
        window.flip()
        if isParallelPort: pport.setData(pportInt)
        core.wait(0.01)
        stimVisual.draw()
        circles[1].draw()
        window.flip()
        if isParallelPort: pport.setData(0)
    elif stimuliType == 'Sound':
        stimVisual = visual.SimpleImageStim(win=window, image=path.join(folderPath,'listen_icon.png'))
        stimVisual.draw()
        circles[0].draw()
        window.flip()
        if isParallelPort: pport.setData(pportInt)
        core.wait(0.05) 
        stimVisual.draw()
        circles[1].draw()
        window.flip()
        if isParallelPort: pport.setData(0)
        Sound.play()
        core.wait(Sound.getDuration()+1) # TODO why plus one   
    elif stimuliType == 'Text':
        stimVisual = visual.TextStim(win=window, text=stimSentence, color='black', height=50)
        stimVisual.draw()
        core.wait(0.5)
        circles[0].draw()
        window.flip()
        if isParallelPort: pport.setData(pportInt)
        core.wait(0.05)
        stimVisual.draw()
        circles[1].draw()
        window.flip()
        if isParallelPort: pport.setData(0)
        core.wait(3.5)

    el2 = time()-tic
    core.wait(cueTime-el2)
    duration = time()-tic
    print('¦--- Cue duration:    ' +  str(duration)[0:7] + '   right: ' + str(cueTime))

    ## RESPONSE
    responseText = visual.TextStim(win=window, text='?', color='black', height=100)

    tic = time()
    responseText.draw()
    window.flip()
    core.wait(0.05)
    responseText.draw()
    circles[1].draw()
    window.flip()
    
    while True:
        if len(event.getKeys(keyList='space')) > 0:
            trialType = "go"
            response_type = "correct"
            duration = time()-tic
            reactionTime = time()
            write_data(filename, onset_tic, duration, trialType, blockName, stimNumber, response_type, reactionTime)
            return [False, False]
        if len(event.getKeys(keyList='x')) > 0:
            trialType = "go"
            response_type = "wrong"
            duration = time()-tic
            reactionTime = time()
            write_data(filename, onset_tic, duration, trialType, blockName, stimNumber, response_type, reactionTime)
            return [False, False]
        if len(event.getKeys(keyList='n')) > 0:
            return [False, True]
        if len(event.getKeys(keyList='q')) > 0:
            return [True, True]

## MAIN
imageFiles = path.join(folderPath,'picture_naming','*.png')
imageList = []
for file in glob(imageFiles): imageList.append(file)

soundFile = path.join(folderPath,'auditory_naming','*.wav')
soundList = []
for file in glob(soundFile): soundList.append(file)

readingList = open(path.join(folderPath,'reading_completion','reading_comp.txt')).read().split('\n')

print('¦...... In folder:  ', folderPath)
print('¦............ Number of Images:  ', len(imageList))
print('¦............ Number of Sounds:  ', len(soundList))

## DIALOG WINDOW
while True:
    dlg = gui.Dlg(title="Functional Language Mapping Initialisation")
    dlg.addField("Subject ID:")
    dlg.addField("Kind of stimuli:", choices=stimuliTypes)
    dlg.addField("Number of block repetition (50 stimuli per block):",1)
    dlg.addField("Use // port for trigger?:", choices=['No', 'Yes'])
    dlg.addField("// port address:", '/dev/parport0')
    dlg.show()
    dlgData = dlg.data
    if dlg.OK:
        subjectId = dlgData[0]
        stimuliType = dlgData[1]
        repeatNum = dlgData[2]
        isParallelPort = (dlgData[3] == 'Yes')
        pportAddress = dlgData[4]
        filename = path.join(resultsPath, 'sub-' + subjectId + '_task-LanguageMapping_events.tsv')

        if path.isfile(filename):
            dlgErrorFileExist = gui.Dlg(title="Error")
            dlgErrorFileExist.addText("Subject name already exists, cannot overwrite")
            dlgErrorFileExist.show()
            doExperiment = False
            break                          
        else:
            with open(filename,'w') as fileData:
                fileData.write('SubjectNumber : ' + subjectId + '\n')
                fileData.write('onset\tduration\ttrialType\tcategory\texemplar\tresponse_type\tresponse_time')
                fileData.write('\n')
            break
    else:
        doExperiment = False
        break

## EXPERIMENT
if doExperiment:
    shallExit = False
    instructionText = '\n\nPress x for bad trial.\nPress space to continue\nPress n to skip the block.\nPress q to quit'
    congratsText = 'Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n'

    pport = None
    if isParallelPort:
        pport = parallel.ParallelPort(address=pportAddress)
        pport.setData(0)

    isImage = False
    isSound = False
    isText = False
    if stimuliType == 'All': # all
        isImage = True
        isSound = True
        isText = True
    elif stimuliType == 'Image': isImage = True
    elif stimuliType == 'Sound': isSound = True
    elif stimuliType == 'Text' : isText  = True
    else: 
        doExperiment = False
        shallExit = True

    # WINDOW INIT
    window = visual.Window([1800,1000], pos=[0,0], monitor="default", waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
    fix = visual.TextStim(win=window, text="+", pos=[0,0], color='black', height=30)
    #circle_black = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1], colorSpace='rgb')
    #circle_gray  = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[0, 0, 0], lineColor=[0, 0, 0], colorSpace='rgb')
    circle_black = visual.Circle(pos=[-900,-480], win=window, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1], colorSpace='rgb')
    circle_gray  = visual.Circle(pos=[-900,-480], win=window, units="pix", radius=60, fillColor=[0, 0, 0], lineColor=[0, 0, 0], colorSpace='rgb')
    circles = [circle_black, circle_gray]

    start_tic = time()
    if not shallExit: 
        visual.SimpleImageStim(win=window, image=instructionsFile).draw()
        window.flip()
        event.waitKeys(keyList='space')

    # TASK BLOCKS
    if isImage and not shallExit:
        introText = 'Picture Naming:\nName the picture when the question mark appears.' + instructionText
        itemList = imageList
        shallExit = task_block(window, fix, circles, 'Image', introText, itemList, start_tic, filename, pport)
    if isSound and not shallExit:
        introText = 'Auditory Naming:\nRespond with the word that best explains the sentence when the question mark appears.' + instructionText
        itemList = soundList
        shallExit = task_block(window, fix, circles, 'Sound', introText, itemList, start_tic, filename, pport)
    if isText and not shallExit:
        introText = 'Reading Sentence Completion:\nRead quietly and complete the sentence vocally to the best of your ability' + instructionText
        itemList = readingList
        shallExit = task_block(window, fix, circles, 'Text', introText, itemList, start_tic, filename, pport)

    # END OF TASKS
    if not shallExit:
        responseText = visual.TextStim(win=window, text="", color='black', height=20)
        responseText.setText(text=congratsText + path.basename(filename))
        responseText.draw()     
        window.flip()
        event.waitKeys(keyList='space')
