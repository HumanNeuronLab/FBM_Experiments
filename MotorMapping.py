import os
import time
import numpy as np
import serial
from psychopy import visual, core, event, gui

# Define block configuration
blocks = [
    ("Hand Movement (Left)", [3.1, 3.2, 3.3, 3.4], 3),
    ("Hand Movement (Right)", [3.1, 3.2, 3.3, 3.4], 3),
    ("Foot Movement (Left)", [3.1, 3.2, 3.3, 3.4], 3),
    ("Foot Movement (Right)", [3.1, 3.2, 3.3, 3.4], 3),
    ("Mouth Movement", [3.1, 3.2, 3.3, 3.4], 3),
]

# Write trial data to a file  
def write_to_file(file_name, data):
    with open(file_name, "a") as file:
        file.write("\t".join(map(str, data)) + "\n")

# Run a single trial
def run_trial(win, fix_black, fix_green, rectangle, baseline_durations, stim_durations, trial_number, block_name, file_name, serial_port):

    if 'q' in event.getKeys(): core.quit()
    
    # Baseline phase
    baseline_duration = np.random.choice(baseline_durations)
    fix_black.draw()
    win.flip()
    if serial_port:
        serial_port.write(bytes(bytearray([7])))  # Send start signal for stimuli phase
    core.wait(baseline_duration)

    # Stimuli phase (3 seconds)
    stim_duration = int(stim_durations)
    print("Trial number: " + str(trial_number) + "   Block name: "+str(block_name))  # Fixed 3 seconds for stimuli
    fix_green.draw()
    rectangle.draw()  # Draw the black circle in the top-left corner
    win.flip()
    if serial_port:
        serial_port.write(bytes(bytearray([9])))  # Send start signal for stimuli phase
    core.wait(stim_duration)

    # Record trial data
    trial_data = [block_name, trial_number, baseline_duration, stim_duration]
    write_to_file(file_name, trial_data)

# Run the motor mapping experiment
def run_motor_mapping(serial_port, experiment_settings):
    # Initialize display window
    win_size=[1920, 1080]
    win = visual.Window(size=win_size, color="white", units="pix", fullscr=True, screen=display_settings["Screen"])  # Full screen mode
    fix_black = visual.TextStim(win, text="+", color="black", height=50)
    fix_green = visual.TextStim(win, text="+", color="green", height=50)
    # Create a black circle stimulus for the top-left corner
    # black_circle = visual.Circle(win, radius=40, fillColor='black', lineColor='black', pos=(-win.size[0]/2 + 40, win.size[1]/2 - 40))  # Adjust position for top-left corner
    rectangle = visual.Rect(
        win=win,
        width=70,
        height=140,
        fillColor="black",
        lineColor="black",
        pos=[-1 * win.size[0] / 2 + 50 / 2,
            win.size[1] / 2 - 100 / 2],
        units="pix"
    )
    
    # four black circles, 0.5 seconds appart
    for i in range(4):
        win.flip()
        core.wait(0.5)
        rectangle.draw()  # Draw the black circle in the top-left corner
        win.flip()
        core.wait(0.5)
   
    # Output file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    results_folder = "Results"

    subject_id = subject_info["Subject ID"]
    file_name = os.path.join(
        results_folder, 
        f"sub-{subject_id}_task-motormapping_datetime-{timestamp}.tsv"
    )

    with open(file_name, "w") as file:
        file.write("Block\tTrial\tBaselineDuration\tStimuliDuration\n")
    
    # Experiment Introduction
    intro_text = f"Welcome to the Motor Mapping Experiment\n\n"
    intro_text += f"Subject ID: {subject_info['Subject ID']}\n"
    intro_text += f"Trigger Type: {subject_info['Trigger Type']}\n"
    intro_text += f"Total Blocks: {len(blocks)}\n\n"
    intro_text += f"Press the space key to begin the experiment."
    
    # Display introduction
    intro_stim = visual.TextStim(win, text=intro_text, color="black", height=30)
    intro_stim.draw()
    win.flip()
    # Before intro wait loop
    event.clearEvents()
    waiting = True
    while waiting:
        keys = event.getKeys()
        if 'space' in keys: waiting = False
        if 'q' in keys: core.quit()
        core.wait(0.01)

    # Run experiment blocks
    for block_name, baseline_durations, stim_durations in blocks:
        if not experiment_settings[block_name]["Run"]:
            continue  # Skip the block if it is unchecked
               
        # Display block instructions
        instructions = visual.TextStim(win, text=f"Starting block: {block_name}\n\nRepeat the movement while + is green", color="black", height=30)
        instructions_image = visual.ImageStim(win,image=os.path.join("images", block_name[0:4]+".png"), size=(300, 300), pos=(0, -250))
        instructions.draw()
        instructions_image.draw()
        win.flip()

        # Wait for "space" response before starting block
        waiting = True
        while waiting == True:
            keys = event.getKeys()
            if 'space' in keys: waiting = False
            if 'q' in event.getKeys(): core.quit()

        # Run trials for the block based on the number of trials provided in experiment_settings
        num_trials = experiment_settings.get(block_name, {}).get("Number of Trials")
        for trial_number in range(1, num_trials + 1):  # Variable number of trials per block
            run_trial(win, fix_black, fix_green, rectangle, baseline_durations, stim_durations, trial_number, block_name, file_name, serial_port)

    # End of experiment
    goodbye_message = visual.TextStim(win, text="Thank you for participating! \nFile name: \n"+file_name, color="black", height=40)
    goodbye_message.draw()
    win.flip()
    core.wait(3)
    win.close()

# Initialize the serial connection
def initialize_serial(portname='0'):
    # Initialize the serial port for triggering
    try:
        port = serial.Serial(portname, 9600, timeout=5)  # Adjust the port name as necessary
        print("Serial connection established.")
        return port
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        return None

# GUI initialization
def initialize_gui():
    dialog = gui.Dlg(title="Motor Mapping Experiment Initialization")
    dialog.addText("Subject Information", color="blue")
    dialog.addField("Subject ID:", 'Test')
    dialog.addField("Trigger Type:", choices=["Photodiode", "Serial", "Parallel"])
    dialog.addField("Choose serial port (if applicable):", 'COM?')
    
    dialog.addText("Choose experiments to run:", color="green")
    dialog.addField("Hand Movement (Left)", initial=True)
    dialog.addField("Hand Movement (Right)", initial=True)
    dialog.addField("Foot Movement (Left)", initial=True)
    dialog.addField("Foot Movement (Right)", initial=True)
    dialog.addField("Mouth Movement", initial=True)
    dialog.addField("Number of trials", '30')
    
    dialog.addText("Display Settings", color="red")
    dialog.addField("Choose screen:", choices=[0, 1, 2])
    dialog.addField("Display resolution:", choices=[[1920, 1080], [1280, 1024], [800, 600]])
    
    dialog.show()
    
    if dialog.OK:
        data = dialog.data
        
        subject_info = {
            "Subject ID": data[0],
            "Trigger Type": data[1],
            "Serial Port": data[2] if data[1] == "Serial" else None
        }

        experiment_settings = {
            "Hand Movement (Left)": {"Run": data[3], "Number of Trials": int(data[8])},
            "Hand Movement (Right)": {"Run": data[4], "Number of Trials": int(data[8])},
            "Foot Movement (Left)": {"Run": data[5], "Number of Trials": int(data[8])},
            "Foot Movement (Right)": {"Run": data[6], "Number of Trials": int(data[8])},
            "Mouth Movement": {"Run": data[7], "Number of Trials": int(data[8])},
        }

        display_settings = {
            "Screen": data[-2],
            "Resolution": data[-1]
        }
        
        return subject_info, experiment_settings, display_settings
    else:
        return None, None, None

# Main execution
if __name__ == "__main__":


    subject_info, experiment_settings, display_settings = initialize_gui()
    
    if not subject_info:
        core.quit()

    # Initialize serial port if required
    serial_port = None
    if subject_info["Trigger Type"] == "Serial":
        serial_port = initialize_serial(subject_info["Serial Port"])

    if serial_port is None and subject_info["Trigger Type"] == "Serial":
        print("Failed to initialize serial port. Exiting experiment.")
        core.quit()

    # Run the motor mapping experiment
    run_motor_mapping(serial_port, experiment_settings)

    # Close the serial connection after the experiment
    if serial_port:
        serial_port.close()
