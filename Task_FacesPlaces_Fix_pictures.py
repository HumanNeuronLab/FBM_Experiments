from psychopy import visual, core, event
import os
import random
from PIL import Image
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Step 1: Initialization parameters- Experiment Setup Dialog
screen_resolution = [1920, 1080]  # Converts selected resolution string to a list [width, height]

# Hide the root Tkinter window
Tk().withdraw()

# Ask the user to select the media folder
media_folder = askdirectory(title="Select Media Folder")

# Validate the folder
if not media_folder:
    print("No folder selected. Exiting.")
    core.quit()

if not os.path.isdir(media_folder):
    print(f"The specified folder '{media_folder}' does not exist.")
    core.quit()

# Set up the experiment directories
main_folder = os.path.dirname(os.path.abspath(__file__))  # Current script location
results_folder = os.path.join(main_folder, "Results")
os.makedirs(results_folder, exist_ok=True)

# Step 2: Load and Randomize Media Files
media_files = [
    f for f in os.listdir(media_folder)
    if f.endswith(('.jpg', '.png', '.jfif', '.mp4', '.avi'))
    ] 
random.shuffle(media_files)

# Calculate square size for cropping
square_size = min(screen_resolution) // 3  # Use 1/3 of the smaller screen dimension

# Function to resize and crop an image to a square
def crop_to_square(image_path, square_size):
    with Image.open(image_path) as img:
        img_width, img_height = img.size

        # First, resize the image to ensure it is smaller than the cropping area
        if img_width > img_height:
            scale_factor = square_size / img_height
        else:
            scale_factor = square_size / img_width

        # Resize with aspect ratio maintained
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # Now calculate the cropping area
        left = (new_width - square_size) // 2
        top = (new_height - square_size) // 2
        right = left + square_size
        bottom = top + square_size

        # Crop the image to the square size
        img = img.crop((left, top, right, bottom))

        # Save the cropped and resized image to a temporary path
        temp_path = os.path.join(media_folder, f"temp_{os.path.basename(image_path)}")
        img.save(temp_path)
        return temp_path

# Process media files
for media_file in media_files:
    if media_file.startswith("temp_") or media_file.startswith("Patient_"):
        print(f"Skipping file: {media_file} (PRE-DONE)")
        continue  # Skip files starting with "temp_"

    media_path = os.path.join(media_folder, media_file)
    cropped_path = crop_to_square(media_path, square_size)
    print(f"Cropped image saved at: {cropped_path}")

core.quit()