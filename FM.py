import os
import glob
import time
import codecs
import numpy as np
import serial
import psychopy
from datetime import datetime
from psychopy import visual, core, event, gui, sound

# Set preferences
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']

# Define global constants and variables
CENTER = [0, 0]
BASE_TIME = [1.1, 1.2, 1.3, 1.4]
CUE_TIME = [1]
RESPONSE_TIME = [2]
TIMING = [BASE_TIME, CUE_TIME, RESPONSE_TIME]
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
RES_PATH = os.path.join(FOLDER_PATH, 'Results')
CHOOSE_EXPERIMENT = ['Picture Naming', 'Auditory Definition', 'Sentence Completion', 'Motor Tasks', 'Category Localizer (Auditory)', 'Category Localizer (Visual)']
CHOOSE_LANGUAGE = [filename[-3:] for filename in glob.glob(os.path.join(FOLDER_PATH, 'auditory_naming_*'))]

now = datetime.now()
timestamp = str(now.hour) + 'h' + str(now.minute) + 'm' + str(now.second) + 's'
now = "-".join([str(now.day), str(now.month), str(now.year)])

def write_to_file(file_name, data):
    with open(file_name, "a") as file:
        file.write("\t".join(data) + '\n')

def initialize_experiment():
    dialog = gui.Dlg(title="Functional Language Mapping Initialization")
    dialog.addText("Subject Information", color="blue")
    dialog.addField("Subject ID:", 'Test')
    dialog.addField("Trigger type?", choices=["Photodiode", "Serial", "Parallel"])
    dialog.addField(" -> Photodiode Position", choices=["top left", "top right", "bottom left", "bottom right"])
    dialog.addField(" -> Serial - [COM3 for example]:", 'COM')
    dialog.addField(" -> Parallel - [0x0378 for example]:", '0x')
    dialog.addField("Choose language:", choices=CHOOSE_LANGUAGE)
    
    dialog.addText("Choose experiments to run:", color="green")
    for exp in CHOOSE_EXPERIMENT:
        dialog.addField(' ' + exp, initial=False)
        dialog.addField('    -> number of trials', choices=[3, 30, 50])

    dialog.addText("Display Settings", color="red")
    dialog.addField("Choose screen:", choices=[0, 1, 2])
    dialog.addField("Display resolution:", choices=[[1920, 1080], [1800, 800], [1280, 1024]])
    dialog.show()

    if dialog.OK:
        data = dialog.data

        # Perform basic validation if nothing is written
        if not data[0]:
            error_dialog = gui.Dlg(title="Error")
            error_dialog.addText("Subject ID cannot be empty.")
            error_dialog.show()
            return initialize_experiment()  # Reopen the dialog

        # Reorganize data into three sections
        subject_info = {
            "Subject ID": data[0],
            "Trigger Type": data[1],
            "Photodiode Position": data[2],
            "Serial Port": data[3] if data[1] == "Serial" else None,
            "Parallel Port": data[4] if data[1] == "Parallel" else None,
            "Language": data[5],
        }

        experiment_settings = {}
        for i, exp in enumerate(CHOOSE_EXPERIMENT):
            experiment_settings[exp] = {
                "Run": data[6 + i * 2],
                "Number of Trials": data[7 + i * 2] if data[6 + i * 2] else None
            }

        display_settings = {
            "Screen": data[-2],
            "Resolution": data[-1]
        }
        return subject_info, experiment_settings, display_settings
    else:
        return None, None, None

def onetrial(win, stim, fix, timing, file_name, trial_number, block_number, is_image=False, is_text=False, is_sound=False, disp_size=0, serial_porting=0):
    square = visual.Rect(
        pos=[(-1 * disp_size[0] / 2) + 150, disp_size[1] / 2 - 75],
        win=win,
        units="pix",
        width=300,
        height=150,
        fillColor=[-1, -1, -1],
        lineColor=[-1, -1, -1]
    )

    event.clearEvents(eventType=None)
    tic = time.time()

    # Determine stimulus details
    if is_sound:
        stim_sound = sound.Sound(stim)
    if not is_text:
        block_name = stim.split('\\')[-2]
        stim_number, stim_name = stim.split('\\')[-1][0:-4].split('_')
    else:
        block_name = 'reading_completion'
        stim_number, stim_sentence, stim_name = stim.split('_')

    # Baseline
    np.random.shuffle(timing[0])
    base_time = timing[0][0]
    cue_time = timing[1][0]
    response_time = timing[2][0]

    fix.draw()
    win.flip()
    core.wait(base_time - (time.time() - tic))

    # Cue
    tic = time.time()
    if is_image:
        stim_visual = visual.SimpleImageStim(win=win, image=stim)
        stim_visual.draw()
        square.draw()
        win.flip()

        if serial_porting != 0:
            serial_porting.write(b'FMvisual')
            time.sleep(1)
            response = serial_porting.read(10)
            print(f"Received: {response}")

        core.wait(1)
    elif is_text:
        stim_visual = visual.TextStim(win=win, text="", color='black', height=50)
        stim_visual.setText(stim_sentence)
        stim_visual.draw()
        square.draw()
        win.flip()
        if serial_porting != 0:
            serial_porting.write(b'FMtext')
        core.wait(3.5 if file_name[-3:] != "GER" else 5.5)
    else:
        fix.draw()
        square.draw()
        win.flip()
        if serial_porting != 0:
            serial_porting.write(b'FM')
        stim_sound.play()
        core.wait(stim_sound.getDuration() + 1)

    core.wait(cue_time - (time.time() - tic))

    # Response
    tic = time.time()  
    response_text = visual.TextStim(win=win, text="?", color='black', height=40)
    response_text.draw()
    win.flip()
    if serial_porting != 0:
        serial_porting.write(b'response')
    response = serial_porting.read(10)
    print(f"Received: {response}")

    quit_now = False
    reaction_time = None
    while True:
        keys = event.getKeys()
        if 'q' in keys or 'num_9' in keys:
            quit_now = True
            if serial_porting != 0:
                serial_porting.write(b'FMquit')
            response = serial_porting.read(10)
            print(f"Received: {response}")
            break
        if 'space' in keys or 'num_4' in keys or '103' in keys:
            reaction_time = time.time() - tic
            if serial_porting != 0:
                serial_porting.write(b'FM+')
            response = serial_porting.read(10)
            print(f"Received: {response}") 
            break
        if 'x' in keys or 'num_6' in keys:
            reaction_time = time.time() - tic
            if serial_porting != 0:
                serial_porting.write(b'FM-')
            break
        if 'n' in keys or 'num_8' in keys:
            if serial_porting != 0:
                serial_porting.write(b'FMskipblock')
            break

    duration = time.time() - tic
    data = [str(tic), str(duration), 'go', block_name, stim_number, 'correct' if reaction_time else 'wrong', str(reaction_time)]
    write_to_file(file_name, data)

    return quit_now

def run_experiment(initial_data):
    if not initial_data:
        return
    
    info_subject, info_experiment, info_displayscreen = initial_data
    now = datetime.now().strftime("%d-%m-%Y_%Hh%Mm%Ss")
    file_name = os.path.join(RES_PATH, f'sub-{info_subject["Subject ID"]}_task-LanguageMapping_timestamp-{now}_lang-{info_subject["Language"]}_events.tsv')

    if info_subject['Trigger Type'] == "Serial":
        PortName = info_subject["Serial Port"]
        port = serial.Serial(PortName, 9600, timeout=5)
        port.write(b'FMstart')
        time.sleep(1)
        response = port.read(10)
        print(f"Received: {response}")
    else:
        port = 0

    with open(file_name, 'w') as file:
        file.write(f'sub- : {info_subject["Subject ID"]}\tlanguage: {info_subject["Language"]}\tdate: {now}\n')
        file.write("onset\tduration\ttrial_type\tblock_name\tstim_number\tstim_response\tstim_rt\n")

    win = visual.Window(size=info_displayscreen["Resolution"], units="pix", color=(1, 1, 1), fullscr=False, screen=info_displayscreen["Screen"])
    fix = visual.TextStim(win, text="+", height=50, color='black')

    for experiment in info_experiment:
        if info_experiment[experiment]["Run"]:
            for trial in range(info_experiment[experiment]["Number of Trials"]):
                quit_now = onetrial(win, fix, TIMING, file_name, trial + 1, experiment, port)
                if quit_now:
                    break

    if port != 0:
        port.write(b'FMquit')
        response = port.read(10)
        print(f"Received: {response}")
        port.close()

initial_data = initialize_experiment()
run_experiment(initial_data)
