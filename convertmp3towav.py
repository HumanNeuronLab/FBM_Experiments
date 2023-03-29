from os import path
from pydub import AudioSegment
import glob

all_files = glob.glob("/Users/lorafanda/Documents/Coding/Experiments_PsychoPy/auditory_naming_de/*.mp3")

for file in all_files:
    sound = AudioSegment.from_mp3(file)
    output_file = file.split('.')[0]+'.wav'
    sound.export(output_file, format="wav")