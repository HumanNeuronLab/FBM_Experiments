import os
import glob
import time
import codecs
import numpy as np
import serial
import psychopy
from datetime import datetime
from psychopy import visual, core, event, gui, sound

#check and delete all:
#response = serial_porting.read(10)  # Adjust the byte size as needed
#print(f"Received: {response}")


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
CHOOSE_EXPERIMENT = ['Picture Naming', 'Auditory Definition', 'Sentence Completion', 'Motor Tasks', 'Category Localizer (Auditory)','Category Localizer (Visual)']
CHOOSE_LANGUAGE = [filename[-3:] for filename in glob.glob(os.path.join(FOLDER_PATH, 'auditory_naming_*'))]

now=datetime.now()
timestamp = str(now.hour)+'h'+str(now.minute)+'m'+str(now.second)+'s'
now="-".join([str(now.day),str(now.month),str(now.year)])

def write_to_file(file_name, data):
    with open(file_name, "a") as file:
        file.write("\t".join(data) + '\n')

def initialize_experiment():
    dialog = gui.Dlg(title="Functional Language Mapping Initialization")
    dialog.addText("Subject Information", color="blue")
    dialog.addField("Subject ID:",'Test')
    dialog.addField("Trigger type?", choices=["Photodiode", "Serial", "Parallel"])
    dialog.addField(" -> Photodiode Position", choices=["top left", "top right", "bottom left", "bottom right"])
    dialog.addField(" -> Serial - [COM3 for example]:", 'COM')
    dialog.addField(" -> Parallel - [0x0378 for example]:", '0x')
    dialog.addField("Choose language:", choices=CHOOSE_LANGUAGE)
    
    dialog.addText("Choose experiments to run:", color="green")
    for exp in CHOOSE_EXPERIMENT:
        dialog.addField(' ' + exp, initial=False)
        dialog.addField('    -> number of trials', choices=[3, 30, 100])

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


def onetrial(win, stim, fix, timing, file_name, trial_number, block_number, is_image=False, is_text=False, is_sound=False, disp_size=0,serial_porting = 0):
    square = visual.Rect(
        pos=[(-1 * disp_size[0] / 2) + 150, disp_size[1] / 2 - 75],
        win=win,
        units="pix",
        width=300,  # Width of the square (equivalent to the circle's diameter)
        height=150,  # Height of the square
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
            serial_porting.write(bytes(bytearray([1])))
            core.wait(1)
    elif is_text:
        stim_visual = visual.TextStim(win=win, text="", color='black', height=50)
        stim_visual.setText(stim_sentence)
        stim_visual.draw()
        square.draw()
        win.flip()
        if serial_porting != 0: 
                serial_porting.write(bytes(bytearray([2])))
        core.wait(file_name[-3:] == "GER" and 5.5 or 3.5)
    else:
        fix.draw()
        square.draw()
        win.flip()
        if serial_porting != 0: serial_porting.write(bytes(bytearray([3])))
        stim_sound.play()
        core.wait(stim_sound.getDuration() + 1)

    core.wait(cue_time - (time.time() - tic))

    # Response
    tic = time.time()  
    response_text = visual.TextStim(win=win, text="?", color='black', height=40)
    response_text.draw()
    win.flip()
    if serial_porting != 0: serial_porting.write(bytes(bytearray([10])))
    # response = serial_porting.read(10)  # Adjust the byte size as needed
    # print(f"Received: {response}")

    quit_now = False
    reaction_time = None
    while True:
        # core.wait(0.2)
        keys = event.getKeys()
        if 'q' in keys or 'num_9' in keys:
            quit_now = False
            # if serial_porting != 0: serial_porting.write(bytes(bytearray([90])))
            # if serial_porting != 0: serial_porting.write(bytes(bytearray([90])))
            # response = serial_porting.read(10)  # Adjust the byte size as needed
            # print(f"Received: {response}")
            break
        if 'space' in keys or 'num_4' in keys or '103' in keys:
            reaction_time = time.time() - tic
            # if serial_porting != 0: serial_porting.write(bytes(bytearray([20])))
            # response = serial_porting.read(10)  # Adjust the byte size as needed
            # print(f"Received: {response}") 
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
        port = serial.Serial(PortName,9600, timeout=5) #COM4 is the right one
        port.write(bytes(bytearray([7])))
    else: 
        port = 0

    with open(file_name, 'w') as file:
        file.write(f'sub- : {info_subject["Subject ID"]}\n')
        file.write('task- : LanguageMapping\n')
        file.write('onset\tduration\ttrial_type\tcategory\texemplar\tresponse_type\tresponse_time\n')

    win = visual.Window(info_displayscreen['Resolution'], pos=[0, 0], monitor="default", screen=info_displayscreen['Screen'], waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
    fix = visual.TextStim(win=win, text="+", pos=[0, 0], color='black', height=30)

    experiments = [
        ('Picture Naming', 'picture_naming', '*.png', True, False, False),
        ('Sentence Completion', 'reading_completion', '*.txt', False, True, False),
        ('Motor Tasks', 'motor_tasks', '*.txt', False, True, False),
        ('Category Localizer (Auditory)', 'auditory_localizer', '*.wav', False, False, True),
        ('Category Localizer (Visual)', 'visual_localizer', '*.png', True, False, False),
    ]
 
    for exp_name, folder, file_pattern, is_image, is_text, is_sound in experiments:
        if info_experiment[exp_name]['Run']:
            print(f"Running {exp_name}...")

            if is_image or is_sound:
                stim_files = glob.glob(os.path.join(FOLDER_PATH, folder, file_pattern))
                np.random.shuffle(stim_files)
            else:
                with codecs.open(os.path.join(FOLDER_PATH, f'{folder}_{info_subject["Language"]}', f'{folder}_{info_subject["Language"]}.txt'), encoding='utf-8') as f:
                    stim_files = f.read().split('\n')
                np.random.shuffle(stim_files)

            intro_text = f"{exp_name}:\nRespond when the question mark (?) appears. Let's start with 3 Training examples.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit"
            intro_stim = visual.TextStim(win=win, text=intro_text, color='black')
            intro_stim.draw()
            win.flip()
            while True:
                if 'space' in event.getKeys() or 'num_4' in event.getKeys():
                    break
                if 'q' in event.getKeys() or 'num_9' in event.getKeys():
                    core.quit()

            count_text = visual.TextStim(win=win, text="", color='black')
            for i in [3, 2, 1]:
                count_text.setText(str(i))
                count_text.draw()
                win.flip()
                core.wait(1)

            for i, stim in enumerate(stim_files[:3]):
                onetrial(win, stim, fix, TIMING, file_name, i+1, 0, is_image=is_image, is_text=is_text, is_sound=is_sound, disp_size=info_displayscreen["Resolution"],serial_porting=port)

            for i, stim in enumerate(stim_files[3:info_experiment[exp_name]['Number of Trials']]):
                onetrial(win, stim, fix, TIMING, file_name, i+1, 1, is_image=is_image, is_text=is_text, is_sound=is_sound, disp_size=info_displayscreen["Resolution"],serial_porting=port)

    win.close()

if __name__ == "__main__":
    initial_data = initialize_experiment()
    if not initial_data:
        core.quit()
    run_experiment(initial_data)
        

