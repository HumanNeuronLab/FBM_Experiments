# CategoryLocalizer_combined.py
# Combines:
#   - CategoryLocalizer_visual.py
#   - CategoryLocalizer_Audio165.py
#
# Minimal changes:
#   1) One GUI dropdown to choose Visual vs Audio165
#   2) Serial triggers changed from letters (b'v', b'b', b'a') to numeric bytes (bytes([..]))
#   3) Everything else kept in the original logic/ordering as much as possible

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
import random

# (kept from your originals)
from pyo import *

# =========================================================
# TRIGGERS: NUMERIC BYTES (EDIT CODES HERE IF NEEDED)
# =========================================================
# Original letters used:
#   b'v' : visual trigger (cue + response in visual; cue for image branch in audio; response in audio)
#   b'b' : audio trigger (audio cue; also sent once after response in audio)
#   b'a' : repeat marker in audio
#
# You said letters aren't accepted -> send numeric bytes instead.
# Choose the numeric codes your acquisition expects:
TRIG_V = 1  # replaces b'v'
TRIG_B = 2  # replaces b'b'
TRIG_A = 3  # replaces b'a'

def send_trig(code):
    # Uses global: WithTriggers, port
    if WithTriggers == 'Yes':
        port.write(bytes([int(code)]))

# =========================================================
# GLOBAL CONSTANTS (kept style from originals)
# =========================================================
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']
Center = [0, 0]
BaseTime = [0.8, 0.9, 1, 1.1]
ResponseTime = [2]  # official

now = datetime.now()
timestamp = str(now.hour) + 'h' + str(now.minute) + 'm' + str(now.second) + 's'
now = "-".join([str(now.day), str(now.month), str(now.year)])

Exp = True
folder_path = os.path.dirname(os.path.abspath(__file__))
Respath = os.path.join(folder_path, 'Results')

# =========================================================
# VISUAL LIST BUILDER (copied logic)
# =========================================================
def build_visual_image_list():
    ImageFiles_scrambled = os.path.join(folder_path, 'CatLocalizer_images', 'scrambled*.png')
    ImageFiles_word = os.path.join(folder_path, 'CatLocalizer_images', 'word*.png')
    ImageFiles_corridor = os.path.join(folder_path, 'CatLocalizer_images', 'corridor*.png')
    ImageFiles_child = os.path.join(folder_path, 'CatLocalizer_images', 'child*.png')
    ImageFiles_car = os.path.join(folder_path, 'CatLocalizer_images', 'car*.png')
    ImageFiles_body = os.path.join(folder_path, 'CatLocalizer_images', 'body*.png')
    ImageFiles_adult = os.path.join(folder_path, 'CatLocalizer_images', 'adult*.png')
    ImageFiles_number = os.path.join(folder_path, 'CatLocalizer_images', 'number*.png')
    ImageFiles_instrument = os.path.join(folder_path, 'CatLocalizer_images', 'instrument*.png')

    image_list = []
    image_list.append(random.sample(glob.glob(ImageFiles_scrambled), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_word), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_corridor), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_child), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_car), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_body), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_adult), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_number), k=30))
    image_list.append(random.sample(glob.glob(ImageFiles_instrument), k=30))
    image_list = [item for sublist in image_list for item in sublist]  # flattens list
    return image_list

# =========================================================
# AUDIO LIST BUILDER (copied logic)
# =========================================================
def build_audio_list_165():
    AudioFiles = os.path.join(folder_path, 'AudCatLoc_natsounds165', 'wav', '*.wav')
    new_audio_list = []
    for filename in glob.glob(AudioFiles):
        new_audio_list.append(filename)
    new_audio_list.sort()

    audio_list = []
    # (kept exactly: single chunk, then random.sample)
    for i in range(0, len(new_audio_list), len(new_audio_list)):
        audio_list.append(random.sample(new_audio_list[i:i + len(new_audio_list)], k=len(new_audio_list)))
    audio_list = [item for sublist in audio_list for item in sublist]
    return audio_list

# =========================================================
# ONETRIAL: VISUAL (copied, only trigger write changed)
# =========================================================
def onetrial_visual(mywin, Stim, fix, rectangle, Timing, FileName,
                   TrialNumber, BlockNumber, isImage=False, isRepeatImage=False,
                   timeOfRepeat=0, start_tic=0):

    quitnow = False
    tic = time.time()
    BlockName = 'CategoryLocalizer'
    Stim1 = Stim.split('\\')[-1]
    StimName, StimNumber = Stim1[0:-4].split('-')

    # 0: Define time durations base, cue and response
    np.random.shuffle(Timing[0])
    BaseTime_ = Timing[0][0]
    CueTime_ = Timing[1][0]
    ResponseTime_ = Timing[2][0]

    ## 1: BASELINE
    fix.draw()
    mywin.flip()
    el1 = time.time() - tic
    core.wait(BaseTime_ - el1)
    print('¦--- Baseline (fix) duration: ' + str(time.time() - tic)[0:7] + '   right: ' + str(BaseTime_))

    ## 2: CUE
    tic = time.time()
    onset_tic = tic - start_tic
    if isImage:
        StimVisual = visual.SimpleImageStim(win=mywin, image=Stim)
        StimVisual.draw()
        rectangle.draw()
        mywin.flip()

        # TRIGGER (was b'v')
        if WithTriggers == 'Yes':
            send_trig(TRIG_V)

        print("¦--- Showing:                ", Stim1, '   Repeat:', isRepeatImage)

    ReactionTime = 0
    ValidTrial = 0
    if isRepeatImage:
        timeOfRepeat = time.time()
    else:
        timeOfRepeat = 0

    el2 = time.time() - tic
    core.wait(CueTime_ - el2)
    duration = time.time() - tic
    sample_offset = str(time.time() + duration)
    print('¦--- Cue (Image) duration:    ' + str(duration)[0:7] + '   right: ' + str(CueTime_))

    ## 3: RESPONSE
    tic = time.time()
    mywin.flip()
    if len(event.getKeys(keyList='q')) > 0 or len(event.getKeys(keyList='num_9')) > 0:
        quitnow = True

    # Save to txt file
    if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')) > 0:  # CORRECT
        if WithTriggers == 'Yes':
            send_trig(TRIG_V)  # (was b'v')
        duration = time.time() - tic
        ReactionTime = time.time()
        sample_offset = str(time.time() + duration)

    if (ReactionTime == 0 and timeOfRepeat == 0) or (ReactionTime != 0 and timeOfRepeat != 0):
        ValidTrial = 1

    if timeOfRepeat != 0:
        trial_type = "go"
        if ReactionTime == 0:
            response_type = "miss"
        else:
            response_type = "hit"
    else:
        trial_type = "no_go"
        if ReactionTime == 0:
            response_type = "correct_rejection"
        else:
            response_type = "false_alarm"

    Resp = [ValidTrial, ReactionTime]
    with open(FileName, "a") as FileData:
        txt = [str(onset_tic)[0:10], str(duration)[0:7], trial_type, StimName, StimNumber, response_type, str(Resp[1])]
        txt = [str(t) for t in txt]
        FileData.write("\t".join(txt))
        FileData.write('\n')

    return quitnow, timeOfRepeat, ReactionTime

# =========================================================
# ONETRIAL: AUDIO165 (copied, only trigger write changed)
# =========================================================
def onetrial_audio165(mywin, Stim, fix, rectangle, Timing, FileName,
                      TrialNumber, BlockNumber, isImage=False, isRepeatImage=False,
                      timeOfRepeat=0, start_tic=0):

    quitnow = False
    tic = time.time()
    BlockName = 'CatLocAudio165'
    Stim1 = Stim.split('\\')[-1]
    Stim1 = Stim1.split('.')[0]
    StimName, StimNumber = Stim1.split('_')[0:2]
    Sound_ = sound.Sound(Stim)

    # 0: Define time durations base, cue and response
    np.random.shuffle(Timing[0])
    BaseTime_ = Timing[0][0]
    CueTime_ = Timing[1][0]
    ResponseTime_ = Timing[2][0]

    ## 1: BASELINE
    fix.draw()
    mywin.flip()
    el1 = time.time() - tic
    core.wait(BaseTime_ - el1)
    print('¦--- Baseline (fix) duration: ' + str(time.time() - tic)[0:7] + '   right: ' + str(BaseTime_))

    ## 2: CUE
    tic = time.time()
    onset_tic = tic - start_tic
    if isImage:  # (kept even if you never use it in audio mode)
        StimVisual = visual.SimpleImageStim(win=mywin, image=Stim)
        StimVisual.draw()
        rectangle.draw()
        mywin.flip()
        core.wait(1)
        if WithTriggers == 'Yes':
            send_trig(TRIG_V)  # (was b'v')
        print("¦--- Showing:                ", Stim1, '   Repeat:', isRepeatImage)
    else:
        fix.draw()
        rectangle.draw()
        mywin.flip()
        # IMPORTANT: keep your original ordering: trigger BEFORE Sound.play()
        if WithTriggers == 'Yes':
            send_trig(TRIG_B)  # (was b'b')
        Sound_.play()
        core.wait(Sound_.getDuration())

    el2 = time.time() - tic
    core.wait(CueTime_ - el2)
    print('¦--- cue duration:      ' + str(time.time() - tic)[0:7] + '   right: ' + str(CueTime_))

    ReactionTime = 0
    ValidTrial = 0
    if isRepeatImage:
        timeOfRepeat = time.time()
        if WithTriggers == 'Yes':
            send_trig(TRIG_A)  # (was b'a')
    else:
        timeOfRepeat = 0

    el2 = time.time() - tic
    core.wait(CueTime_ - el2)
    duration = time.time() - tic
    sample_offset = str(time.time() + duration)
    print('¦--- Cue (Image) duration:    ' + str(duration)[0:7] + '   right: ' + str(CueTime_))

    tic = time.time()
    if len(event.getKeys(keyList='q')) > 0 or len(event.getKeys(keyList='num_9')) > 0:
        quitnow = True

    if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')) > 0:
        if WithTriggers == 'Yes':
            send_trig(TRIG_V)  # (was b'v')
        duration = time.time() - tic
        ReactionTime = time.time()
        sample_offset = str(time.time() + duration)
        if WithTriggers == 'Yes':
            send_trig(TRIG_B)  # (was b'b')  <-- kept because your audio script did this

    if (ReactionTime == 0 and timeOfRepeat == 0) or (ReactionTime != 0 and timeOfRepeat != 0):
        ValidTrial = 1

    if timeOfRepeat != 0:
        trial_type = "go"
        if ReactionTime == 0:
            response_type = "miss"
        else:
            response_type = "hit"
    else:
        trial_type = "no_go"
        if ReactionTime == 0:
            response_type = "correct_rejection"
        else:
            response_type = "false_alarm"

    Resp = [ValidTrial, ReactionTime]
    with open(FileName, "a") as FileData:
        txt = [str(onset_tic)[0:10], str(duration)[0:7], trial_type, StimName, StimNumber, response_type, str(Resp[1])]
        txt = [str(t) for t in txt]
        FileData.write("\t".join(txt))
        FileData.write('\n')

    return quitnow, timeOfRepeat, ReactionTime

# =========================================================
# GUI: ONE DROPDOWN TO CHOOSE MODALITY
# =========================================================
while True:
    DlgInit = gui.Dlg(title="Category Localizer Initialisation")
    DlgInit.addField("Stimulus modality:", choices=["Visual", "Audio165"])  # <-- requested dropdown
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Volume (0-1): ", 1)
    DlgInit.addField("PORT (COM): ", 'COM3')
    DlgInit.addField("Use serial triggers?: ", choices=["No", "Yes"])
    DlgInit.addField("Choose screen: ", choices=[0, 1, 2])
    DlgInit.addField("Display resolution: ", choices=[[1920, 1080], [1800, 800], [1280, 1024]])
    DlgInit.show()

    InitialData = DlgInit.data
    if DlgInit.OK:
        modality = InitialData[0]  # "Visual" or "Audio165"
        SbjNumber = InitialData[1]
        Volume = InitialData[2]
        PortName = InitialData[3]
        WithTriggers = InitialData[4]
        choice_screen = InitialData[5]
        disp_size = InitialData[6]

        if modality == "Visual":
            FileName = 'sub-' + SbjNumber + '_task-LocalizerVisual_timestamp-' + now + '(' + timestamp + ')_events.tsv'
        else:
            FileName = 'sub-' + SbjNumber + '_task-LocalizerAud165_timestamp-' + now + '(' + timestamp + ')_events.tsv'

        FileName = os.path.join(Respath, FileName)

        if os.path.isfile(FileName):
            DlgFile = gui.wx.MessageDialog(
                None,
                "File exist. Do you want to continue or define other parameters(yes) or overwrite file(no)",
                style=gui.wx.YES | gui.wx.NO | gui.wx.ICON_QUESTION
            )
            Resp = DlgFile.ShowModal()
            if Resp == 5103:
                with open(FileName, 'w') as FileData:
                    FileData.write('\n')
                    FileData.write('sub- : ' + SbjNumber + '\n')
                    if modality == "Visual":
                        FileData.write('task- : LocalizerVisual\n')
                    else:
                        FileData.write('task- : LocalizerAud165\n')
                    FileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time')
                    FileData.write('\n')
                break
        else:
            os.makedirs(Respath, exist_ok=True)
            with open(FileName, 'w') as FileData:
                FileData.write('SubjectNumber : ' + SbjNumber + '\n')
                FileData.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time')
                FileData.write('\n')
            break
    else:
        Exp = False
        break

# =========================================================
# START THE EXPERIMENT (branch by modality)
# =========================================================
if Exp:
    if WithTriggers == 'Yes':
        port = serial.Serial(PortName, 9600, timeout=5)
        port.readData

    # modality-specific stimulus list + timing + visuals
    if modality == "Visual":
        CueTime = [1]  # from visual script
        Timing = [BaseTime, CueTime, ResponseTime]

        image_list = build_visual_image_list()
        print('¦. Folder Used is:  ', folder_path)
        print('¦. Number of Images:  ', np.size(image_list), '\n')

        mywin = visual.Window(
            disp_size, pos=[0, 0], monitor="default", screen=choice_screen,
            waitBlanking=True, units="pix", color='gray', fullscr=True, allowGUI=True
        )
        fix = visual.TextStim(win=mywin, text="+", pos=[0, 0], color='black', height=30)
        repeatNum = 1

        rectangle = visual.Rect(
            win=mywin, width=70, height=140,
            fillColor="black", lineColor="black",
            pos=[-1 * disp_size[0] / 2 + 50 / 2, disp_size[1] / 2 - 100 / 2],
            units="pix"
        )

        core.wait(2)
        pd_flash = 5
        interval = 0.2

        def flash_start_end_signal(win, rectangle, pd_flash, interval=0.3):
            for _ in range(pd_flash):
                rectangle.draw()
                win.flip()
                core.wait(interval)
                win.flip()
                core.wait(interval)

        flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
        print(f"Category Localizer Visual Experiment Begins! Photodiode flashed {pd_flash} times at interval {interval} (s)")

        Exit = False
        IntroText = visual.TextStim(win=mywin, text="", color='black')
        IntroText.setText(text='Category Localizer Visual:\n\n Press SPACE BAR or numpad 4 when you see a repeating image. \n\nPress q to quit')
        IntroText.draw()
        mywin.flip()
        while True:
            if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')) > 0:
                break

        CountText = visual.TextStim(win=mywin, text="", color='black')
        Count = [3, 2, 1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)

        np.random.shuffle(image_list)
        repeatIndex = [False for i in range(len(image_list))]
        new_i = random.randrange(5, 16)
        old_image_list = image_list
        for i, item in enumerate(old_image_list):
            if i < new_i:
                continue
            rand_index = random.randrange(5, 16)
            print(i, new_i, rand_index)
            print(' ')
            image_list.insert(i, image_list[i - 1])
            repeatIndex.insert(i, True)
            new_i = i + rand_index

        onset = time.time()
        timeOfRepeat = 0
        ReactTime = 0
        start_tic = time.time()

        for i, s in enumerate(image_list):
            if Exit or len(event.getKeys(keyList='q')) > 0:
                break
            print('\nTrial ' + str(i + 1) + ' of ' + str(len(image_list)) + '¦ ')
            Exit, timeOfRepeat, ReactTime = onetrial_visual(
                mywin, s, fix, rectangle, Timing, FileName, i + 1, 0,
                isImage=True, isRepeatImage=repeatIndex[i],
                timeOfRepeat=timeOfRepeat, start_tic=start_tic
            )
            print("Reaction Time (if not repeat, its 0 0): ", ReactTime, timeOfRepeat)

        flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
        print(f"Category Localizer Visual Experiment ENDS! Photodiode flashed {pd_flash} times at interval {interval} (s)")

        ResponseText = visual.TextStim(win=mywin, text="", color='black', height=20)
        ResponseText.setText(text='Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n...' + FileName[-50:-1])
        ResponseText.draw()
        mywin.flip()
        while True:
            if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')):
                break
            if len(event.getKeys(keyList='q')) > 0:
                exit()

    else:
        # Audio165 branch
        CueTime = [2]  # from audio165 script
        Timing = [BaseTime, CueTime, ResponseTime]

        audio_list = build_audio_list_165()
        print('¦...... Folder Used is:  ', folder_path)
        print('¦............ Number of Sounds:  ', np.size(audio_list))

        mywin = visual.Window(
            disp_size, pos=[0, 0], monitor="default", screen=choice_screen,
            waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True
        )
        fix = visual.TextStim(win=mywin, text="+", pos=[0, 0], color='black', height=30)
        repeatNum = 1

        rectangle = visual.Rect(
            win=mywin, width=70, height=140,
            fillColor="black", lineColor="black",
            pos=[-1 * disp_size[0] / 2 + 50 / 2, disp_size[1] / 2 - 100 / 2],
            units="pix"
        )

        core.wait(2)
        pd_flash = 10
        interval = 0.1

        def flash_start_end_signal(win, rectangle, pd_flash, interval=0.3):
            for _ in range(pd_flash):
                rectangle.draw()
                win.flip()
                core.wait(interval)
                win.flip()
                core.wait(interval)

        flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
        print(f"Category Localizer Audio Experiment Begins! Photodiode flashed {pd_flash} times at interval {interval} (s)")

        Exit = False
        IntroText = visual.TextStim(win=mywin, text="", color='black')
        IntroText.setText(text='Category Localizer Audio 165:\n\n Press SPACE BAR or numpad 4 when you see a repeating sound. \n\nPress q  or numpad 9 to quit')
        IntroText.draw()
        mywin.flip()
        while True:
            if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')) > 0:
                break
            if len(event.getKeys(keyList='q')) > 0 or len(event.getKeys(keyList='num_9')) > 0:
                exit()

        CountText = visual.TextStim(win=mywin, text="", color='black')
        Count = [3, 2, 1]
        for i in Count:
            CountText.setText(text=i)
            CountText.draw()
            mywin.flip()
            core.wait(1)

        np.random.shuffle(audio_list)
        repeatIndex = [False for i in range(len(audio_list))]
        new_i = random.randrange(4, 14)
        old_audio_list = audio_list
        for i, item in enumerate(old_audio_list):
            if i < new_i:
                continue
            rand_index = random.randrange(4, 14)
            audio_list.insert(i, audio_list[i - 1])
            repeatIndex.insert(i, True)
            new_i = i + rand_index

        onset = time.time()
        timeOfRepeat = 0
        ReactTime = 0
        start_tic = time.time()

        for i, s in enumerate(audio_list):
            if Exit or len(event.getKeys(keyList='q')) > 0 or len(event.getKeys(keyList='num_9')) > 0:
                break
            print('\nTrial ' + str(i + 1) + ' of ' + str(len(audio_list)) + '¦ ')
            Exit, timeOfRepeat, ReactTime = onetrial_audio165(
                mywin, s, fix, rectangle, Timing, FileName, i + 1, 0,
                isImage=False, isRepeatImage=repeatIndex[i],
                timeOfRepeat=timeOfRepeat, start_tic=start_tic
            )
            print("Reaction Time (if not repeat, its 0 0): ", ReactTime, timeOfRepeat)

        flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
        print(f"Category Localizer Audio Experiment ENDS! Photodiode flashed {pd_flash} times at interval {interval} (s)")

        ResponseText = visual.TextStim(win=mywin, text="", color='black', height=20)
        ResponseText.setText(text='Congrats! \nYou are done!\n\nPress SPACE BAR to end the experiment \n\nData saved as: \n...' + FileName[-50:-1])
        ResponseText.draw()
        mywin.flip()
        while True:
            if len(event.getKeys(keyList='space')) > 0 or len(event.getKeys(keyList='num_4')):
                break
            if len(event.getKeys(keyList='q')) > 0 or len(event.getKeys(keyList='num_9')) > 0:
                exit()