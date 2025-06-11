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
CHOOSE_EXPERIMENT = ['Memory Pictures', 'Memory Words', 'Memory Sounds']
now = datetime.now()
timestamp = str(now.hour) + 'h' + str(now.minute) + 'm' + str(now.second) + 's'
now = "-".join([str(now.day), str(now.month), str(now.year)])

def write_to_file(file_name, data):
    with open(file_name, "a") as file:
        file.write("\t".join(data) + '\n')

def initialize_experiment():
    dialog = gui.Dlg(title="Memory Experiment Initialization")
    dialog.addText("Subject Information", color="blue")
    dialog.addField("Subject ID:", 'Test')
    dialog.addField("Trigger type?", choices=["Serial"])
    dialog.addField(" -> Serial - [COM3 for example]:", 'COM')
    
    dialog.addText("Choose experiments to run:", color="green")
    # Dynamically create checkboxes for each experiment
    experiment_checkbox_fields = {}
    for exp in CHOOSE_EXPERIMENT:
        experiment_checkbox_fields[exp] = dialog.addField(f' {exp}', initial=False)

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
            "Serial Port": data[3] if data[1] == "Serial" else None,
            "Parallel Port": data[4] if data[1] == "Parallel" else None,
        }

        # Get the boolean values of the checkboxes
        experiment_settings = {}
        for exp in CHOOSE_EXPERIMENT:
            experiment_settings[exp] = {
                "Run": data[experiment_checkbox_fields[exp]] == 'True'  # Check if checkbox is selected
            }

        display_settings = {
            "Screen": data[-2],
            "Resolution": data[-1]
        }
        return subject_info, experiment_settings, display_settings
    else:
        return None, None, None

def get_trial_count(folder_name, file_pattern):
    """Count the total number of files within the given folder and subfolders."""
    path = os.path.join(FOLDER_PATH, folder_name, file_pattern)
    files = glob.glob(path, recursive=True)
    return len(files)

def onetrial(win, stim, fix, timing, file_name, trial_number, block_number, is_image=False, is_text=False, is_sound=False, disp_size=0, serial_porting=0):

    event.clearEvents(eventType=None)
    tic = time.time()

    # Determine stimulus details
    if is_sound:
        stim_sound = sound.Sound(stim)
    if not is_text:
        block_name = stim.split('\\')[-2]
        stim_number, stim_name = stim.split('\\')[-1][0:-4].split('_')
    else:
        block_name = 'memory_words'
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
        win.flip()
        core.wait(1)
    elif is_text:
        stim_visual = visual.TextStim(win=win, text="", color='black', height=50)
        stim_visual.setText(stim_sentence)
        stim_visual.draw()
        win.flip()
        core.wait(3.5)
    else:
        fix.draw()
        win.flip()
        stim_sound.play()
        core.wait(stim_sound.getDuration() + 1)

    # Response
    tic = time.time()  
    response_text = visual.TextStim(win=win, text="?", color='black', height=40)
    response_text.draw()
    win.flip()

    quit_now = False
    reaction_time = None
    while True:
        core.wait(0.2)
        keys = event.getKeys()
        if 'q' in keys or 'num_9' in keys:
            quit_now = True
            break
        if 'space' in keys:
            reaction_time = time.time() - tic
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
    file_name = os.path.join(RES_PATH, f'sub-{info_subject["Subject ID"]}_task-MemoryMapping_timestamp-{now}_events.tsv')

    if info_subject['Trigger Type'] == "Serial":
        PortName = info_subject["Serial Port"]
        port = serial.Serial(PortName, 9600, timeout=5)  # COM4 is the right one
        port.write(bytes(bytearray([7])))
    else:
        port = 0

    with open(file_name, 'w') as file:
        file.write(f'sub- : {info_subject["Subject ID"]}\n')
        file.write('task- : MemoryMapping\n')
        file.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time\n')

    win = visual.Window(info_displayscreen['Resolution'], pos=[0, 0], monitor="default", screen=info_displayscreen['Screen'], waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
    fix = visual.TextStim(win=win, text="+", pos=[0, 0], color='black', height=30)

    experiments = [
        ('Memory Pictures', 'memory_pictures', '*.png', True, False, False),
        ('Memory Words', 'memory_words', '*.txt', False, True, False),
        ('Memory Sounds', 'memory_sounds', '*.wav', False, False, True)
    ]
    
    for exp_name, folder, file_pattern, is_image, is_text, is_sound in experiments:
        if info_experiment[exp_name]["Run"]:
            trial_count = get_trial_count(folder, file_pattern)

            for trial in range(trial_count):
                stim_file = os.path.join(FOLDER_PATH, folder, f"{trial+1:03d}_{exp_name}.file")  # Example of choosing files
                quit_now = onetrial(win, stim_file, fix, TIMING, file_name, trial + 1, 1, is_image, is_text, is_sound)
                if quit_now:
                    break
    win.close()

# Initialize and run the experiment
initial_data = initialize_experiment()
run_experiment(initial_data)
