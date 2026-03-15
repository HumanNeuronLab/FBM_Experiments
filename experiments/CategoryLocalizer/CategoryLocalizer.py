"""
MIT License

Copyright (c) 2026 Lora Fanda
See LICENSE file in the project root for full license information.
"""
import os
import glob
import time
import random
import serial
import numpy as np
from datetime import datetime
import psychopy

psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']

from psychopy import visual, core, event, gui, sound


Center = [0, 0]
BaseTime = [0.8, 0.9, 1, 1.1]
ResponseTime = [2]  # official

now_dt = datetime.now()
timestamp = f"{now_dt.hour}h{now_dt.minute}m{now_dt.second}s"
now = f"{now_dt.day}-{now_dt.month}-{now_dt.year}"
Exp = True

folder_path = os.path.dirname(os.path.abspath(__file__))


# =========================
# PATH HELPERS
# =========================
def first_existing_path(candidates, kind="path"):
    for p in candidates:
        if kind == "dir" and os.path.isdir(p):
            return p
        if kind == "file" and os.path.isfile(p):
            return p
        if kind == "glob" and len(glob.glob(p)) > 0:
            return p
    return None


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


# Running from parent CategoryLocalizer folder:
# try both local and subfolder locations so the script is robust.
RES_CANDIDATES = [
    os.path.join(folder_path, "Results"),
    os.path.join(folder_path, "Visual", "Results"),
    os.path.join(folder_path, "Audio", "Results"),
]

VISUAL_STIM_CANDIDATES = [
    os.path.join(folder_path, "CatLocalizer_images"),
    os.path.join(folder_path, "Visual", "CatLocalizer_images"),
]

AUDIO_STIM_CANDIDATES = [
    os.path.join(folder_path, "AudCatLoc_natsounds165"),
    os.path.join(folder_path, "Audio", "AudCatLoc_natsounds165"),
]

Respath = first_existing_path(RES_CANDIDATES, kind="dir")
if Respath is None:
    Respath = ensure_dir(os.path.join(folder_path, "Results"))

VisualStimRoot = first_existing_path(VISUAL_STIM_CANDIDATES, kind="dir")
AudioStimRoot = first_existing_path(AUDIO_STIM_CANDIDATES, kind="dir")


# =========================
# GUI
# =========================
while True:
    DlgInit = gui.Dlg(title="Category Localizer Initialisation")
    DlgInit.addField("Subject ID:")
    DlgInit.addField("Localizer modality: ", choices=["Visual", "Audio"])
    DlgInit.addField("Volume (0-1): ", 1)
    DlgInit.addField("PORT (COM): ", "COM3")
    DlgInit.addField("Use serial triggers?: ", choices=["No", "Yes"])
    DlgInit.addField("Choose screen: ", choices=[0, 1, 2])
    DlgInit.addField("Display resolution: ", choices=[[1920, 1080], [1800, 800], [1280, 1024]])
    DlgInit.show()
    InitialData = DlgInit.data

    if not DlgInit.OK:
        Exp = False
        break

    SbjNumber = InitialData[0]
    LocalizerModality = InitialData[1]
    Volume = InitialData[2]
    PortName = InitialData[3]
    WithTriggers = InitialData[4]
    choice_screen = InitialData[5]
    disp_size = InitialData[6]

    if LocalizerModality == "Visual":
        TASK_LABEL = "CategoryLocalizerVisual"
        BLOCK_NAME = "CategoryLocalizerVisual"
        INTRO_TEXT = (
            "Category Localizer Visual:\n\n"
            "Press SPACE BAR or numpad 4 when you see a repeating image.\n\n"
            "Press q or numpad 9 to quit"
        )
        CUE_TRIGGER = bytes(bytearray([1]))
        STIM_OFFSET_TRIGGER = bytes(bytearray([10]))

        REPEAT_MIN = 5
        REPEAT_MAX = 16
        CueTime = [1]

        if VisualStimRoot is None:
            raise FileNotFoundError("Could not find the visual stimulus folder (CatLocalizer_images).")

        ImageFiles_scrambled = os.path.join(VisualStimRoot, "scrambled*.png")
        ImageFiles_word = os.path.join(VisualStimRoot, "word*.png")
        ImageFiles_corridor = os.path.join(VisualStimRoot, "corridor*.png")
        ImageFiles_child = os.path.join(VisualStimRoot, "child*.png")
        ImageFiles_car = os.path.join(VisualStimRoot, "car*.png")
        ImageFiles_body = os.path.join(VisualStimRoot, "body*.png")
        ImageFiles_adult = os.path.join(VisualStimRoot, "adult*.png")
        ImageFiles_number = os.path.join(VisualStimRoot, "number*.png")
        ImageFiles_instrument = os.path.join(VisualStimRoot, "instrument*.png")

        stim_list = []
        stim_list.append(random.sample(glob.glob(ImageFiles_scrambled), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_word), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_corridor), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_child), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_car), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_body), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_adult), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_number), k=30))
        stim_list.append(random.sample(glob.glob(ImageFiles_instrument), k=30))
        stim_list = [item for sublist in stim_list for item in sublist]

        bg_color = "gray"
        pd_flash = 5
        interval = 0.2

    else:
        TASK_LABEL = "CategoryLocalizerAudio"
        BLOCK_NAME = "CategoryLocalizerAudio"
        INTRO_TEXT = (
            "Category Localizer Audio:\n\n"
            "Press SPACE BAR or numpad 4 when you hear a repeating sound.\n\n"
            "Press q or numpad 9 to quit"
        )
        CUE_TRIGGER = bytes(bytearray([2]))
        STIM_OFFSET_TRIGGER = bytes(bytearray([10]))
        REPEAT_MIN = 4
        REPEAT_MAX = 14
        CueTime = [2]

        if AudioStimRoot is None:
            raise FileNotFoundError("Could not find the audio stimulus folder (AudCatLoc_natsounds165).")

        AudioFiles = os.path.join(AudioStimRoot, "wav", "*.wav")
        new_audio_list = sorted(glob.glob(AudioFiles))
        stim_list = random.sample(new_audio_list, k=len(new_audio_list))

        bg_color = "white"
        pd_flash = 10
        interval = 0.1

    Timing = [BaseTime[:], CueTime, ResponseTime]

    FileName = f"sub-{SbjNumber}_task-{TASK_LABEL}_timestamp-{now}({timestamp})_events.tsv"
    FileName = os.path.join(Respath, FileName)

    print("¦...... Folder Used is: ", folder_path)
    print("¦...... Results Folder: ", Respath)
    print("¦...... Localizer modality: ", LocalizerModality)
    print("¦............ Number of Stimuli: ", np.size(stim_list))

    if os.path.isfile(FileName):
        DlgFile = gui.wx.MessageDialog(
            None,
            "File exists. Do you want to continue and overwrite it (no), or define other parameters (yes)?",
            style=gui.wx.YES | gui.wx.NO | gui.wx.ICON_QUESTION
        )
        Resp = DlgFile.ShowModal()
        if Resp == 5103:
            with open(FileName, "w") as FileData:
                FileData.write("\n")
                FileData.write("sub- : " + SbjNumber + "\n")
                FileData.write("task- : " + TASK_LABEL + "\n")
                FileData.write("onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time\n")
            break
    else:
        with open(FileName, "w") as FileData:
            FileData.write("SubjectNumber : " + SbjNumber + "\n")
            FileData.write("onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time\n")
        break


# =========================
# HELPERS
# =========================
def flash_start_end_signal(win, rectangle, pd_flash, interval=0.3):
    for _ in range(pd_flash):
        rectangle.draw()
        win.flip()
        core.wait(interval)
        win.flip()
        core.wait(interval)


def parse_stim_info(stim_path, modality):
    stim_base = os.path.basename(stim_path)

    if modality == "Visual":
        stim_name, stim_number = os.path.splitext(stim_base)[0].split("-")
    else:
        stim_base_noext = os.path.splitext(stim_base)[0]
        parts = stim_base_noext.split("_")
        stim_name = parts[0]
        stim_number = parts[1] if len(parts) > 1 else "NA"

    return stim_base, stim_name, stim_number


def build_repeat_sequence(base_list, min_gap, max_gap):
    seq = list(base_list)
    random.shuffle(seq)

    repeat_index = [False for _ in range(len(seq))]
    new_i = random.randrange(min_gap, max_gap)

    old_seq = list(seq)
    for i, item in enumerate(old_seq):
        if i < new_i:
            continue
        rand_index = random.randrange(min_gap, max_gap)
        seq.insert(i, seq[i - 1])
        repeat_index.insert(i, True)
        new_i = i + rand_index

    return seq, repeat_index


def onetrial(
    mywin,
    Stim,
    fix,
    rectangle,
    Timing,
    FileName,
    TrialNumber,
    BlockNumber,
    modality="Visual",
    isRepeatStim=False,
    timeOfRepeat=0,
    start_tic=0,
):
    quitnow = False
    tic = time.time()

    Stim1, StimName, StimNumber = parse_stim_info(Stim, modality)

    np.random.shuffle(Timing[0])
    BaseTime = Timing[0][0]
    CueTime = Timing[1][0]
    ResponseTime = Timing[2][0]

    # 1) BASELINE
    fix.draw()
    if WithTriggers == "Yes":
        mywin.callOnFlip(port.write, STIM_OFFSET_TRIGGER)
    mywin.flip()
    el1 = time.time() - tic
    if BaseTime - el1 > 0:
        core.wait(BaseTime - el1)
    print("¦--- Baseline (fix) duration: " + str(time.time() - tic)[0:7] + "   right: " + str(BaseTime))

    # 2) CUE
    tic = time.time()
    onset_tic = tic - start_tic

    if modality == "Visual":
        StimVisual = visual.SimpleImageStim(win=mywin, image=Stim)
        StimVisual.draw()
        rectangle.draw()
        if WithTriggers == "Yes":
            mywin.callOnFlip(port.write, CUE_TRIGGER)
        mywin.flip()
        print("¦--- Showing: ", Stim1, "   Repeat:", isRepeatStim)

    else:
        StimSound = sound.Sound(Stim)
        StimSound.setVolume(Volume)
        fix.draw()
        rectangle.draw()

        next_flip = mywin.getFutureFlipTime(clock="ptb")
        StimSound.play(when=next_flip)

        if WithTriggers == "Yes":
            mywin.callOnFlip(port.write, CUE_TRIGGER)

        mywin.flip()
        core.wait(StimSound.getDuration())
        print("¦--- Playing: ", Stim1, "   Repeat:", isRepeatStim)

    ReactionTime = 0
    ValidTrial = 0

    if isRepeatStim:
        timeOfRepeat = time.time()
        if WithTriggers == "Yes":
            port.write(bytes(bytearray([11])))
    else:
        timeOfRepeat = 0

    el2 = time.time() - tic
    if CueTime - el2 > 0:
        core.wait(CueTime - el2)

    duration = time.time() - tic
    print("¦--- Cue duration: " + str(duration)[0:7] + "   right: " + str(CueTime))

    # 3) RESPONSE
    tic = time.time()
    fix.draw()
    mywin.flip()

    if len(event.getKeys(keyList=["q"])) > 0 or len(event.getKeys(keyList=["num_9"])) > 0:
        quitnow = True

    if len(event.getKeys(keyList=["space"])) > 0 or len(event.getKeys(keyList=["num_4"])) > 0:
        ReactionTime = time.time()

    if (ReactionTime == 0 and timeOfRepeat == 0) or (ReactionTime != 0 and timeOfRepeat != 0):
        ValidTrial = 1

    if timeOfRepeat != 0:
        trial_type = "go"
        response_type = "miss" if ReactionTime == 0 else "hit"
    else:
        trial_type = "no_go"
        response_type = "correct_rejection" if ReactionTime == 0 else "false_alarm"

    Resp = [ValidTrial, ReactionTime]
    with open(FileName, "a") as FileData:
        txt = [
            str(onset_tic)[0:10],
            str(duration)[0:7],
            trial_type,
            StimName,
            StimNumber,
            response_type,
            str(Resp[1]),
        ]
        txt = [str(t) for t in txt]
        FileData.write("\t".join(txt))
        FileData.write("\n")

    return quitnow, timeOfRepeat, ReactionTime


# =========================
# START THE EXPERIMENT
# =========================
if Exp:
    if WithTriggers == "Yes":
        port = serial.Serial(PortName, 9600, timeout=5)

    mywin = visual.Window(
        disp_size,
        pos=[0, 0],
        monitor="default",
        screen=choice_screen,
        waitBlanking=True,
        units="pix",
        color=bg_color,
        fullscr=True,
        allowGUI=True,
    )

    fix = visual.TextStim(win=mywin, text="+", pos=[0, 0], color="black", height=30)

    rectangle = visual.Rect(
        win=mywin,
        width=70,
        height=140,
        fillColor="black",
        lineColor="black",
        pos=[-1 * disp_size[0] / 2 + 50 / 2, disp_size[1] / 2 - 100 / 2],
        units="pix",
    )

    core.wait(2)

    flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
    print(f"{TASK_LABEL} begins. Photodiode flashed {pd_flash} times at interval {interval} s")

    # 1) INTRO
    Exit = False
    IntroText = visual.TextStim(win=mywin, text="", color="black")
    IntroText.setText(text=INTRO_TEXT)
    IntroText.draw()
    mywin.flip()

    while True:
        if len(event.getKeys(keyList=["space"])) > 0 or len(event.getKeys(keyList=["num_4"])) > 0:
            break
        if len(event.getKeys(keyList=["q"])) > 0 or len(event.getKeys(keyList=["num_9"])) > 0:
            exit()

    # 2) EXPERIMENT
    CountText = visual.TextStim(win=mywin, text="", color="black")
    for i in [3, 2, 1]:
        CountText.setText(text=i)
        CountText.draw()
        mywin.flip()
        core.wait(1)

    stim_list_run, repeatIndex = build_repeat_sequence(stim_list, REPEAT_MIN, REPEAT_MAX)

    onset = time.time()
    timeOfRepeat = 0
    ReactTime = 0
    start_tic = time.time()

    for i, s in enumerate(stim_list_run):
        if Exit or len(event.getKeys(keyList=["q"])) > 0 or len(event.getKeys(keyList=["num_9"])) > 0:
            break

        print("\nTrial " + str(i + 1) + " of " + str(len(stim_list_run)) + "¦ ")
        Exit, timeOfRepeat, ReactTime = onetrial(
            mywin=mywin,
            Stim=s,
            fix=fix,
            rectangle=rectangle,
            Timing=Timing,
            FileName=FileName,
            TrialNumber=i + 1,
            BlockNumber=0,
            modality=LocalizerModality,
            isRepeatStim=repeatIndex[i],
            timeOfRepeat=timeOfRepeat,
            start_tic=start_tic,
        )
        print("Reaction Time (if not repeat, its 0 0): ", ReactTime, timeOfRepeat)

    flash_start_end_signal(mywin, rectangle, pd_flash=pd_flash, interval=interval)
    print(f"{TASK_LABEL} ends. Photodiode flashed {pd_flash} times at interval {interval} s")

    # 3) END
    ResponseText = visual.TextStim(win=mywin, text="", color="black", height=20)
    ResponseText.setText(
        text="Congrats!\nYou are done!\n\nPress SPACE BAR to end the experiment\n\nData saved as:\n..." + FileName[-100:-1]
    )
    ResponseText.draw()
    mywin.flip()

    while True:
        if len(event.getKeys(keyList=["space"])) > 0 or len(event.getKeys(keyList=["num_4"])) > 0:
            break
        if len(event.getKeys(keyList=["q"])) > 0 or len(event.getKeys(keyList=["num_9"])) > 0:
            exit()

    mywin.close()
    core.quit()