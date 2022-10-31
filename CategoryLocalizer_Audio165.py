from os import path
from glob import glob
import time
from numpy import random as np_random
from psychopy import prefs, visual, core, event, gui, sound, parallel
from pyo import *

# Hardcoded values
prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
folderPath = path.dirname(path.abspath(__file__))
resultsPath = path.join(folderPath,'Results')
pportInt = int("00000101", 2)  # pins 2 and 4 high

baseTime = [0.2]
cueTime = [2] # the sounds are 2s long
responseTime = [2]
timing = [baseTime,cueTime,responseTime]
Exp = True
repeatNum = 1 # how many repetitions of each item

def countdown(window):
    countText = visual.TextStim(win=window, text="", color=[0,0,0])
    for t in [3, 2, 1]:
        countText.setText(text=t)
        countText.draw()
        window.flip()
        core.wait(1)

def write_data(filename, onsetTic, duration, trialType, blockName, stimNumber, responseType, reactionTime):
    print('¦----- reactionTime: ' + str(reactionTime)[0:7])

    with open(filename,"a") as fileData:
        txt = [str(onsetTic), str(duration)[0:7], trialType, blockName, stimNumber, responseType, str(reactionTime)]
        txt = [str(t) for t in txt]
        fileData.write("\t".join(txt))
        fileData.write('\n')

def task_block(window, fix, circles, introText, itemList, filename, pport):
    visual.TextStim(win=window, text=introText, color='black').draw()
    window.flip()

    event.waitKeys(keyList='space')
    countdown(window)

    stopExp = False
    stopBlock = False

    np_random.shuffle(itemList)
    repeatIndex = [False for i in range(len(itemList))]
    new_i = random.randrange(5, 16)
    oldItemList = itemList
    for i, item in enumerate(oldItemList):
        if i < new_i: 
            continue
        rand_index = random.randrange(5, 16)
        itemList.insert(i, itemList[i-1])
        repeatIndex.insert(i, True)
        new_i = i + rand_index

    startTic = time.time()

    for i, item in enumerate(itemList):
        print('\nTrial ' + str(i+1) + '¦ ')
        stopExp, stopBlock = one_trial(window, fix, circles, item,  startTic, filename, pport, repeatIndex[i])
        if stopBlock: return stopExp

    visual.TextStim(win=window, text='Task has ended.\n\nPress space to continue', color='black').draw()     
    window.flip()

    event.waitKeys(keyList='space')

    return stopExp

def one_trial(window, fix, circles, item, startTic, filename, pport, isRepeatImage=False):
    # return [stopExp, stopBlock]   
    tic = time.time()
    event.clearEvents()

    blockName = 'CatLocAudio165'
    tmp = path.basename(item)
    tmp = tmp.split('.')[0]
    stimName, stimNumber = tmp.split('_')[0:2]
    Sound = sound.Sound(item) 
    
    np_random.shuffle(timing[0])
    baseTime = timing[0][0]
    cueTime = timing[1][0] # Cue is always only the first value
    
    ## BASELINE
    circles[1].draw()
    fix.draw()
    window.flip()
    el1 = time.time()-tic
    core.wait(baseTime-el1)
    print('¦--- Baseline (fix) duration: ' + str(time.time()-tic)[0:7] + '   right: ' + str(baseTime))

    ## CUE
    tic = time.time()
    onsetTic = tic - startTic

    stimVisual = visual.SimpleImageStim(win=window, image=path.join(folderPath,'audio_icon.png'))
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
    core.wait(Sound.getDuration())

    print("¦--- Showing:                ", tmp, '   Repeat:', isRepeatImage)
    reactionTime = 0
    timeOfRepeat = 0
    if isRepeatImage: timeOfRepeat = time.time()

    el2 = time.time()-tic
    core.wait(cueTime-el2)
    duration = time.time()-tic
    print('¦--- Cue (Audio) duration:    ' +  str(duration)[0:7] + '   right: ' + str(cueTime))

    ## RESPONSE
    tic = time.time()
    window.flip()

    if len(event.getKeys(keyList='q')) > 0:
        return [True, True]

    if len(event.getKeys(keyList='space')) > 0:
        duration = time.time()-tic
        reactionTime = time.time()

    if timeOfRepeat != 0:
        trialType = "go"
        if reactionTime == 0: responseType = "miss"
        else: responseType = "hit"
    else:
        trialType = "no_go"
        if reactionTime == 0: responseType = "correct_rejection"
        else: responseType = "false_alarm"

    write_data(filename, onsetTic, duration, trialType, blockName, stimNumber, responseType, reactionTime)

    return [False, False]

## MAIN
audioFiles = path.join(folderPath, 'AudCatLoc_natsounds165', 'wav','*.wav')

newAudioList = []
for filename in glob(audioFiles): 
    newAudioList.append(filename)

newAudioList.sort()
audioList = []
for i in range(0, len(newAudioList), 165):
    audioList.append(random.sample(newAudioList[i:i+165], k=165))
audioList = [item for sublist in audioList for item in sublist]# Display relevant information

print('¦...... In folder:  ', folderPath)
print('¦............ Number of Sounds:  ', len(audioList))

## DIALOG WINDOW
while True:
    DlgInit = gui.Dlg(title="Category Localizer (Audio165) Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Use // port for trigger?:", choices=['No', 'Yes'])
    DlgInit.addField("// port address:", '/dev/parport0')
    DlgInit.show()
    InitialData = DlgInit.data
    if DlgInit.OK:
        subjectId = InitialData[0]
        isParallelPort = (InitialData[1] == 'Yes')
        pportAddress = InitialData[2]

        filename = path.join(resultsPath, 'sub-' + subjectId + '_task-LocalizerAud165_events.tsv')

        if path.isfile(filename):
            DlgErrorFileExist = gui.Dlg(title="Error")
            DlgErrorFileExist.addText("Subject name already exists, cannot overwrite")
            DlgErrorFileExist.show()
            Exp = False
            break                          
        else:
            with open(filename,'w') as fileData:
                fileData.write('SubjectNumber : ' + subjectId + '\n')
                fileData.write('onset\tduration\ttrialType\tcategory\texemplar\tresponseType\tresponse_time')
                fileData.write('\n')
            break
    else:
        Exp = False
        break

## EXPERIMENT
if Exp:
    shallExit = False
    instructionText = '\n\nPress SPACE BAR when you see a repeating image.\n\nPress q to quit'
    congratsText = 'Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n'

    pport = None
    if isParallelPort:
        pport = parallel.ParallelPort(address=pportAddress)
        pport.setData(0)

    # WINDOW INIT
    window = visual.Window([1800,1000], pos=[0,0], monitor="default", waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
    fix = visual.TextStim(win=window, text="+", pos=[0,0], color='black', height=30)
    #circle_black = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1], colorSpace='rgb')
    #circle_gray  = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[0, 0, 0], lineColor=[0, 0, 0], colorSpace='rgb')
    circle_black = visual.Circle(pos=[-900,-480], win=window, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1], colorSpace='rgb')
    circle_gray  = visual.Circle(pos=[-900,-480], win=window, units="pix", radius=60, fillColor=[0, 0, 0], lineColor=[0, 0, 0], colorSpace='rgb')
    circles = [circle_black, circle_gray]

    # TASK BLOC
    introText = 'Category Localizer - Audio 165.' + instructionText
    itemList = audioList
    shallExit = task_block(window, fix, circles, introText, itemList, filename, pport)

    # END OF TASKS
    if not shallExit:
        responseText = visual.TextStim(win=window, text="", color='black', height=20)
        responseText.setText(text=congratsText + path.basename(filename))
        responseText.draw()     
        window.flip()
        event.waitKeys(keyList='space')