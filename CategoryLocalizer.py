from os import path
from glob import glob
from time import time
from numpy import random as np_random
from pyo import random
from psychopy import prefs, visual, core, event, gui, parallel

###   Details CHANGE TEXT FILE NAMES
# Define the hardcoded values
prefs.hardware['audioLib'] = ['PTB', 'sounddevice','pyo','pygame']
folderPath = path.dirname(path.abspath(__file__))
resultsPath = path.join(folderPath,'Results')
pportInt = int("00000101", 2)  # pins 2 and 4 high

baseTime = [0.2]
cueTime = [0.8]
responseTime = [2]
timing = [baseTime, cueTime, responseTime]
Exp = True
repeatNum = 1 # how many repetitions of each item

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

    start_tic = time()

    for i, item in enumerate(itemList):
        print('\nTrial ' + str(i+1) + '¦ ')
        stopExp, stopBlock = one_trial(window, fix, circles, item,  start_tic, filename, pport, repeatIndex[i])
        if stopBlock: return stopExp

    visual.TextStim(win=window, text='Task has ended.\n\nPress space to continue', color='black').draw()     
    window.flip()

    event.waitKeys(keyList='space')

    return stopExp

def one_trial(window, fix, circles, item, start_tic, filename, pport, isRepeatImage=False):
    # return [stopExp, stopBlock]
    tic = time()
    event.clearEvents()
    
    tmp = path.basename(item)
    stimName, stimNumber = tmp[0:-4].split('-')
    blockName = 'CategoryLocalizer'
    
    np_random.shuffle(timing[0])
    baseTime = timing[0][0]
    cueTime = timing[1][0] # Cue is always only the first value
    
    ## BASELINE
    circles[1].draw()
    fix.draw()
    window.flip()
    el1 = time()-tic
    core.wait(baseTime-el1)
    print('¦--- Baseline (fix) duration: ' + str(time()-tic)[0:7] + '   right: ' + str(baseTime))

    ## CUE
    tic = time()
    onset_tic = tic - start_tic

    stimVisual = visual.SimpleImageStim(win=window,image=item)
    stimVisual.draw()
    circles[0].draw()
    window.flip()
    if isParallelPort: pport.setData(pportInt)
    core.wait(0.02)
    stimVisual.draw()
    circles[1].draw()
    window.flip()
    if isParallelPort: pport.setData(0)
    
    print("¦--- Showing:                ", tmp, '   Repeat:', isRepeatImage)
    reactionTime = 0
    timeOfRepeat = 0
    if isRepeatImage: timeOfRepeat = time()

    el2 = time()-tic
    core.wait(cueTime-el2)
    duration = time()-tic
    print('¦--- Cue (Image) duration:    ' +  str(duration)[0:7] + '   right: ' + str(cueTime))

    ## RESPONSE
    tic = time()
    window.flip()

    if len(event.getKeys(keyList='q')) > 0: 
        return [True, True]

    if len(event.getKeys(keyList='space')) > 0:
        duration = time()-tic
        reactionTime = time()

    if timeOfRepeat != 0:
        trialType = "go"
        if reactionTime == 0: response_type = "miss"
        else: response_type = "hit"
    else:
        trialType = "no_go"
        if reactionTime == 0: response_type = "correct_rejection"
        else: response_type = "false_alarm"

    write_data(filename, onset_tic, duration, trialType, blockName, stimNumber, response_type, reactionTime)

    return [False, False]

## MAIN
imageFiles = path.join(folderPath,'CatLocalizer_images','*.png')
newImageList = []
for filename in glob(imageFiles): newImageList.append(filename)

newImageList.sort()
imageList = []
for i in range(0, len(newImageList), 144):
    imageList.append(random.sample(newImageList[i:i+144], k=30))
imageList = [item for sublist in imageList for item in sublist]# Display relevant information

print('¦...... In folder:  ', folderPath)
print('¦............ Number of Images:  ', len(imageList))

## DIALOG WINDOW
while True:
    DlgInit = gui.Dlg(title="Category Localizer (Visual) Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Use // port for trigger?:", choices=['No', 'Yes'])
    DlgInit.addField("// port address:", '/dev/parport0')
    DlgInit.show()
    InitialData = DlgInit.data
    if DlgInit.OK:
        SbjNumber = InitialData[0]
        isParallelPort = (InitialData[1] == 'Yes')
        pportAddress = InitialData[2]
        filename = path.join(resultsPath, 'sub-' + SbjNumber + '_task-LocalizerVisual_events.tsv')

        if path.isfile(filename):
            DlgErrorFileExist = gui.Dlg(title="Error")
            DlgErrorFileExist.addText("Subject name already exists, cannot overwrite")
            DlgErrorFileExist.show()
            Exp = False
            break                          
        else:
            with open(filename, 'w') as fileData:
                fileData.write('SubjectNumber : ' + SbjNumber + '\n')
                fileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time')
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
    circle_black = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1], colorSpace='rgb')
    circle_gray  = visual.Circle(pos=[-900,480], win=window, units="pix", radius=60, fillColor=[0, 0, 0], lineColor=[0, 0, 0], colorSpace='rgb')
    circles = [circle_black, circle_gray]

    # TASK BLOCKS
    introText = 'Category Localizer - Visual.' + instructionText
    itemList = imageList
    shallExit = task_block(window, fix, circles, introText, itemList, filename, pport)

    # END OF TASKS
    if not shallExit:
        responseText = visual.TextStim(win=window, text="", color='black', height=20)
        responseText.setText(text=congratsText + path.basename(filename))
        responseText.draw()     
        window.flip()
        event.waitKeys(keyList='space')