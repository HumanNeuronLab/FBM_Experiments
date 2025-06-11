import numpy as np
from psychopy import visual, core, event, gui
import os
import random
import datetime
import serial
from PIL import Image

# --- Experiment Setup Dialog ---
exp_info = {
    "Experiment Name": "patient01",
    "Screen": ["Primary Screen (0)", "Secondary Screen (1)"],
    "Display resolution:": [[1920, 1080], [1800, 800], [1280, 1024]],
    "Serial triggers? (Photodiode always on)": ["No", "Yes"],
    "Port Name": "COM*"
}

dlg = gui.Dlg(title="Experiment Setup")
dlg.addField("Experiment Name:", exp_info["Experiment Name"])
dlg.addField("Screen:", choices=exp_info["Screen"])
dlg.addField("Display resolution:", choices=exp_info["Display resolution:"])
dlg.addField("Serial:", choices=exp_info["Serial triggers? (Photodiode always on)"])
dlg.addField("Port Name", exp_info["Port Name"])

user_input = dlg.show()
if not dlg.OK:
    core.quit()

# --- Parse Inputs ---
exp_name = user_input[0]
screen_choice = 0 if user_input[1] == "Primary Screen (0)" else 1
screen_resolution = user_input[2]
serial_trigs = user_input[3]

if serial_trigs == "Yes":
    PortName = user_input[4]
    port = serial.Serial(PortName, 9600, timeout=5)
    port.write(bytes(bytearray([7])))
else:
    port = 0

# --- Directory Setup ---
main_folder = os.path.dirname(os.path.abspath(__file__))
media_folder = os.path.join(main_folder, "memory_media")
results_folder = os.path.join(main_folder, "Results")
os.makedirs(results_folder, exist_ok=True)

# --- Load Stimuli ---
image_files = [f for f in os.listdir(media_folder) if f.endswith(('.jpg', '.png'))]
if not image_files:
    print("No image files found.")
    core.quit()

word_list = []
for fname in ["temp_words.txt", "Patient_words.txt"]:
    path = os.path.join(media_folder, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            word_list.extend([line.strip() for line in f if line.strip()])

# Step 1: Shuffle original stimuli
stimuli = [{'type': 'image', 'content': f} for f in image_files] + \
          [{'type': 'word', 'content': w} for w in word_list]
random.shuffle(stimuli)

# Step 2: Double all stimuli (for repetition), then re-shuffle
all_stimuli = [stim.copy() for stim in stimuli for _ in range(2)]
random.shuffle(all_stimuli)

# Step 3: No need for repeat flags — we can label all as non-repeats
final_stimuli = all_stimuli
repeat_flags = [False] * len(final_stimuli)

# --- Create Stimulus Sequence with 1-Back Repeats ---
import itertools

# Step 2: Generate repeat indices using cumulative sum of gaps
gaps = [random.randint(5, 15) for _ in range(len(stimuli) // 10)]
repeat_indices = list(itertools.accumulate(gaps))
repeat_indices = [idx for idx in repeat_indices if idx < len(stimuli) - 1]

# Step 3: Create final_stimuli with 1-back repeats
final_stimuli = [
    stim
    for i, stim in enumerate(stimuli)
    for stim in ([stim, stim.copy()] if i in repeat_indices else [stim])
]

repeat_flags = [
    flag
    for i in range(len(stimuli))
    for flag in ([False, True] if i in repeat_indices else [False])
]

# --- PsychoPy Window ---
win = visual.Window(
    size=screen_resolution,
    monitor="testMonitor",
    screen=screen_choice,
    waitBlanking=True,
    units="pix",
    color='black',
    fullscr=True,
    allowGUI=True
)

# # --- Visual Elements ---
# circle_diameter_pixels = 50
# circle = visual.Circle(
#     win,
#     radius=circle_diameter_pixels,
#     fillColor="white",
#     lineColor="white",
#     pos=[-1 * screen_resolution[0] / 2 + circle_diameter_pixels,
#          screen_resolution[1] / 2 - circle_diameter_pixels],
#     units="pix"
# )

rectangle = visual.Rect(
    win,
    width=70,
    height=140,
    fillColor="white",
    lineColor="white",
    pos=[-1 * screen_resolution[0] / 2 + 50 / 2,
         screen_resolution[1] / 2 - 100 / 2],
    units="pix"
)

fixation = visual.TextStim(win, text="+", color='white', height=60)
core.wait(1)
pd_flash =5
def flash_start_end_signal(win, rectangle, pd_flash,interval=0.3):
    for _ in range(pd_flash):
        rectangle.draw()
        win.flip()
        core.wait(interval)
        win.flip()
        core.wait(interval)
# --- Flash Circle Before Start ---
flash_start_end_signal(win, rectangle,pd_flash=pd_flash)
print(f"Faces Places Experiment Begins! Photodiode flashed {pd_flash} times")

core.wait(1)

# --- Results File ---
subject_id_clean = exp_name.replace(" ", "").lower()
timestamp_for_file = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
results_filename = f"sub-{subject_id_clean}_task-facesplaces_{timestamp_for_file}.tsv"
results_file_path = os.path.join(results_folder, results_filename)

# --- Trial Loop ---
with open(results_file_path, "w", encoding="utf-8") as results_file:
    results_file.write("Trial\tStimulusType\tContent\tIsRepeat\tStimuliDuration(s)\tTimeStamp\tFixationDuration(s)\n")

    for idx, (stim, is_repeat) in enumerate(zip(final_stimuli, repeat_flags), start=1):

        if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
            win.close()
            core.quit()

        # --- Fixation (no rectangle) ---
        fixation.draw()
        win.flip()
        fix_time = random.choice([0.5, 0.6, 0.7])
        core.wait(fix_time)

        if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
            win.close()
            core.quit()

        display_length = 1.5
        stim_clock = core.Clock()
        response_made = False
        rt = ""

        event.clearEvents(eventType='keyboard')

        try:
            if stim['type'] == 'image':
                media_path = os.path.join(media_folder, stim['content'])
                with Image.open(media_path) as img:
                    img_width, img_height = img.size
                max_side = max(img_width, img_height)
                adjusted_size = (max_side, max_side)

                stimulus = visual.ImageStim(
                    win,
                    image=media_path,
                    size=adjusted_size if img_width != img_height else None
                )

                while stim_clock.getTime() < display_length:
                    if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
                        win.close()
                        core.quit()
                    keys = event.getKeys(timeStamped=stim_clock)
                    if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
                        response_made = True
                        rt = round(keys[1], 3)
                        print(rt)
                    stimulus.draw()
                    rectangle.draw()
                    win.flip()

            elif stim['type'] == 'word':
                word_stim = visual.TextStim(
                    win,
                    text=stim['content'].split("_")[1],
                    color='white',
                    height=60,
                    wrapWidth=screen_resolution[0] * 0.8
                )

                while stim_clock.getTime() < display_length:
                    if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
                        win.close()
                        core.quit()
                    keys = event.getKeys(timeStamped=stim_clock)
                    if 'escape' in event.getKeys() or 'q' in event.getKeys() or 'num_9' in event.getKeys():
                        response_made = True
                        rt = round(keys[1], 3)
                        print(rt)
                    word_stim.draw()
                    rectangle.draw()
                    win.flip()

            # --- Log Trial Info ---
            stim_type = stim['type']
            content = stim['content']
            repeat_str = "Yes" if is_repeat else "No"
            response_str = "Yes" if response_made else "No"
            log_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            rt_str = str(rt) if response_made else ""
            print(f"Trial {idx} of {len(final_stimuli)}:   {stim}")
            results_file.write(f"{idx}\t{stim_type}\t{content}\t{repeat_str}\t{display_length:.2f}\t{log_time}\t{fix_time}\n")

        except Exception as e:
            print(f"Error displaying stimulus {stim}: {e}")
            continue

# --- Flash Circle After End ---
flash_start_end_signal(win, rectangle,pd_flash=pd_flash)
print(f"Faces Places Experiment Ends! Photodiode flashed {pd_flash} times")
# --- Close Everything ---
win.close()
core.quit()
