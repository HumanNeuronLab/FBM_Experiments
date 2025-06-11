
from psychopy import gui, visual, core, event
import os, glob, codecs
import numpy as np

# Define your experiment options
EXPERIMENT_OPTIONS = ["Picture Naming", "Auditory Naming", "Reading Sentence Completion"]

# Create a dictionary to hold experiment selections
exp_selections = {exp: False for exp in EXPERIMENT_OPTIONS}

# Create a dialog box
dialog = gui.Dlg(title="Experiment Setup")
dialog.addText("Choose experiments to run:")
for exp in EXPERIMENT_OPTIONS:
    dialog.addField(exp, initial=False)

dialog.show()

# If the user cancels the dialog, exit
if not dialog.OK:
    core.quit()

# Update exp_selections based on user input
for i, exp in enumerate(EXPERIMENT_OPTIONS):
    exp_selections[exp] = dialog.data[i]

# Define function to check if any experiment is selected
def any_experiment_selected(exp_selections):
    return any(exp_selections.values())

# Check if any experiment is selected
if not any_experiment_selected(exp_selections):
    print("No experiment selected. Exiting.")
    core.quit()

# Load file paths and other initial setup based on user input
folder_path = "your_folder_path_here"
Selected_language = "your_language_here"
SoundFile = os.path.join(folder_path, 'auditory_naming_' + Selected_language, '*.wav')
ImageFiles = os.path.join(folder_path, 'picture_naming', '*.png')
reading_list = codecs.open(os.path.join(folder_path, 'reading_completion_' + Selected_language, 'reading_comp_' + Selected_language + '.txt'), encoding='utf-8').read().split('\n')

image_list = glob.glob(ImageFiles)
sound_list = glob.glob(SoundFile)

# Initialize the window
disp_size = [800, 600]
choice_screen = 0
mywin = visual.Window(disp_size, pos=[0, 0], monitor="default", screen=choice_screen, waitBlanking=True, units="pix", color='white', fullscr=True, allowGUI=True)
fix = visual.TextStim(win=mywin, text="+", pos=[0, 0], color='black', height=30)

repeatNum = 1  # how many repetitions of each item

# Define a function to run one trial
def onetrial(win, stim, fix, timing, filename, trial_num, block_num, isImage=False, isSound=False, isText=False):
    # Implement the function based on your trial requirements
    return False

# Define timing and filename variables for use in trials
Timing = None  # Replace with actual timing
FileName = "your_file_name_here"  # Replace with actual file name

# Experiment logic based on selections
if exp_selections["Picture Naming"]:
    print("Running Picture Naming...")
    # Show intro and instructions for Picture Naming
    IntroText = visual.TextStim(win=mywin, text="Picture Naming:\nName the picture when the question mark appears. Let's start with 3 Training examples.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit", color='black')
    IntroText.draw()
    mywin.flip()
    while True:
        if 'space' in event.getKeys() or 'num_4' in event.getKeys():
            break
        if 'q' in event.getKeys() or 'num_9' in event.getKeys():
            core.quit()
    
    # Training countdown
    CountText = visual.TextStim(win=mywin, text="", color='black')
    for i in [3, 2, 1]:
        CountText.setText(str(i))
        CountText.draw()
        mywin.flip()
        core.wait(1)
    
    # Shuffle and run training trials
    np.random.shuffle(image_list)
    for i, img in enumerate(image_list[:3]):  # Limiting to 3 training examples
        onetrial(mywin, img, fix, Timing, FileName, i+1, 0, isImage=True)
    
    # Main trials
    for n in range(repeatNum):
        np.random.shuffle(image_list)
        for i, img in enumerate(image_list):
            onetrial(mywin, img, fix, Timing, FileName, i+1, n+1, isImage=True)

if exp_selections["Auditory Naming"]:
    print("Running Auditory Naming...")
    # Show intro and instructions for Auditory Naming
    IntroText = visual.TextStim(win=mywin, text="Auditory Naming:\nRespond with the word that best explains the sentence when the question mark appears. Let's start with 3 Training examples.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit", color='black')
    IntroText.draw()
    mywin.flip()
    while True:
        if 'space' in event.getKeys() or 'num_4' in event.getKeys():
            break
        if 'q' in event.getKeys() or 'num_9' in event.getKeys():
            core.quit()
    
    # Training countdown
    CountText = visual.TextStim(win=mywin, text="", color='black')
    for i in [3, 2, 1]:
        CountText.setText(str(i))
        CountText.draw()
        mywin.flip()
        core.wait(1)
    
    # Shuffle and run training trials
    np.random.shuffle(sound_list)
    for i, snd in enumerate(sound_list[:3]):  # Limiting to 3 training examples
        onetrial(mywin, snd, fix, Timing, FileName, i+1, 0, isSound=True)
    
    # Main trials
    for n in range(repeatNum):
        np.random.shuffle(sound_list)
        for i, snd in enumerate(sound_list):
            onetrial(mywin, snd, fix, Timing, FileName, i+1, n+1, isSound=True)

if exp_selections["Reading Sentence Completion"]:
    print("Running Reading Sentence Completion...")
    # Show intro and instructions for Reading Sentence Completion
    IntroText = visual.TextStim(win=mywin, text="Reading Sentence Completion:\nRead quietly and complete the sentence vocally to the best of your ability.\n\nPress x or numpad 6 for bad trial.\nPress space or numpad 4 to continue\nPress n or numpad 8 to skip the block.\nPress q or numpad 9 to quit", color='black')
    IntroText.draw()
    mywin.flip()
    while True:
        if 'space' in event.getKeys() or 'num_4' in event.getKeys():
            break
        if 'q' in event.getKeys() or 'num_9' in event.getKeys():
            core.quit()
    
    # Training countdown
    CountText = visual.TextStim(win=mywin, text="", color='black')
    for i in [3, 2, 1]:
        CountText.setText(str(i))
        CountText.draw()
        mywin.flip()
        core.wait(1)
    
    # Shuffle and run training trials
    np.random.shuffle(reading_list)
    for i, txt in enumerate(reading_list[:3]):  # Limiting to 3 training examples
        onetrial(mywin, txt, fix, Timing, FileName, i+1, 0, isText=True)
    
    # Main trials
    for n in range(repeatNum):
        np.random.shuffle(reading_list)
        for i, txt in enumerate(reading_list):
            onetrial(mywin, txt, fix, Timing, FileName, i+1, n+1, isText=True)

# End of task message
ResponseText = visual.TextStim(win=mywin, text="Congrats! You are done!\n\nPress SPACE BAR to end the experiment\n\nData saved as:\n...your_file_name_here", color='black', height=20)
ResponseText.draw()
mywin.flip()
while True:
    if 'space' in event.getKeys() or 'num_4' in event.getKeys():
        break
    if 'q' in event.getKeys() or 'num_9' in event.getKeys():
        core.quit()

mywin.close()
core.quit()
