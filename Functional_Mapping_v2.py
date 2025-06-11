import os
import glob
import time
import codecs
import numpy as np
import serial
import psychopy
# Set preferences
psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']
from datetime import datetime
from psychopy import visual, core, event, gui, sound
from collections import namedtuple


# Define global constants and variables
CENTER = [0, 0]
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
RES_PATH = os.path.join(FOLDER_PATH, 'Results')
CHOOSE_EXPERIMENT = ['Picture Naming', 'Auditory Definition', 'Sentence Completion', 'Motor Tasks', 'Category Localizer (Auditory)','Category Localizer (Visual)']
CHOOSE_LANGUAGE = [filename[-3:] for filename in glob.glob(os.path.join(FOLDER_PATH, 'auditory_naming_*'))]

now=datetime.now()
timestamp = str(now.hour)+'h'+str(now.minute)+'m'+str(now.second)+'s'
now="-".join([str(now.day),str(now.month),str(now.year)])

# Named tuple for better structure and readability
Experiment = namedtuple('Experiment', ['name', 'folder', 'file_pattern', 'is_image', 'is_text', 'is_sound', 'baseline_values', 'stim_duration'])

experiments = [
    Experiment('Picture Naming', 'picture_naming', '*.png', True, False, False, [1.1, 1.2, 1.3, 1.4], [1]),
    Experiment('Auditory Definition', 'auditory_naming', '*.wav', False, True, False, [1.1, 1.2, 1.3, 1.4], [2]),
    Experiment('Sentence Completion', 'reading_completion', '*.txt', False, True, False, [1.1, 1.2, 1.3, 1.4], [3.5]),
    Experiment('Motor Tasks', 'motor_tasks',  'N/A', False, True, False, [2.5, 3, 3.5], [3]),
    Experiment('Category Localizer (Auditory)', 'AudCatLoc_natsounds165', '*.wav', False, False, True, [0.8, 0.9, 1, 1.1], [2]),
    Experiment('Category Localizer (Visual)', 'visual_localizer', '*.png', True, False, False, [0.8, 0.9, 1, 1.1], [0.8]),
]

def write_to_file(file_name, data):
    with open(file_name, "a") as file:
        file.write("\t".join(data) + '\n')

def initialize_experiment():
    dialog = gui.Dlg(title="Functional Language Mapping Initialization")
    dialog.addText("Subject Information", color="blue")
    dialog.addField("Subject ID:")
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

        # Perform basic validation
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


# Define a single trial
def onetrial(win, stim, fix, baseline, stim_duration, file_name, trial_number, block_number, is_image=False, is_text=False, is_sound=False, disp_size=[1920, 1080]):
    circle = visual.Circle(pos=[(-1 * disp_size[0] / 2) + 40, disp_size[1] / 2 - 40], win=win, units="pix", radius=60, fillColor=[-1, -1, -1], lineColor=[-1, -1, -1])
    event.clearEvents(eventType=None)
    tic = time.time()

    if is_sound:
        stim_sound = sound.Sound(stim)

    np.random.shuffle(baseline)
    base_time = baseline[0]
    fix.draw()
    win.flip()
    core.wait(base_time - (time.time() - tic))

    tic = time.time()
    if is_image:
        stim_visual = visual.SimpleImageStim(win=win, image=stim)
        stim_visual.draw()
        circle.draw()
        win.flip()
        core.wait(stim_duration[0])
    elif is_text:
        with open(stim, 'r', encoding='utf-8') as f:
            text_content = f.read()
        stim_visual = visual.TextStim(win=win, text=text_content, color='black', height=50)
        stim_visual.draw()
        circle.draw()
        win.flip()
        core.wait(stim_duration[0])
    elif is_sound:
        fix.draw()
        circle.draw()
        win.flip()
        stim_sound.play()
        core.wait(stim_sound.getDuration() + stim_duration[0])

    response_text = visual.TextStim(win=win, text="?", color='black', height=40)
    response_text.draw()
    win.flip()

    quit_now = False
    reaction_time = None
    while True:
        keys = event.getKeys()
        if 'q' in keys or 'num_9' in keys:
            quit_now = True
            core.quit()
            break
        if 'space' in keys or 'num_4' in keys:
            reaction_time = time.time() - tic
            break
    duration = time.time() - tic
    data = [str(tic), str(duration), 'go', stim, 'correct' if reaction_time else 'wrong', str(reaction_time)]
    write_to_file(file_name, data)
    return quit_now

# Run experiments
def run_experiment(info_subject, info_experiment, info_displayscreen):
    win = visual.Window(info_displayscreen['Resolution'], pos=[0, 0], monitor="default", screen=info_displayscreen['Screen'], waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
    fix = visual.TextStim(win=win, text="+", pos=[0, 0], color='black', height=35)

    for experiment in experiments:
        exp_name = experiment.name
        if info_experiment[exp_name]['Run']:
            stim_files = glob.glob(os.path.join(FOLDER_PATH, experiment.folder, experiment.file_pattern)) if experiment.file_pattern != 'N/A' else []
            np.random.shuffle(stim_files)

            for i, stim in enumerate(stim_files[:info_experiment[exp_name]['Number of Trials']]):
                quit_now = onetrial(
                    win, stim, fix, experiment.baseline_values, experiment.stim_duration, 
                    f"{info_subject['Subject ID']}_results.tsv", i+1, 1,
                    is_image=experiment.is_image, is_text=experiment.is_text, is_sound=experiment.is_sound
                )
                if quit_now:
                    break
    win.close()


# Main execution
if __name__ == "__main__":
    initial_data = initialize_experiment()
    if not initial_data:
        core.quit()
    info_subject, info_experiment, info_displayscreen = initial_data
    run_experiment(info_subject, info_experiment, info_displayscreen)
    