<img width="360" height="309" alt="image" src="https://github.com/user-attachments/assets/17c18468-0d33-4094-a157-daf197ad5bf5" />

# FBM Toolkit Experiments  

Experiments for the Human Neuron Lab (HNL) are in the "experiments" folder. All relevand documents will be in the "docs" folder.

**Contact**  
Pierre Megevand – pierre.megevand@unige.ch  
Lora Fanda – lorafanda7@gmail.com  


## 1. Demo Video
[▶️ Click to watch/download](docs/Demo_Video.mp4)


## 2. How to Run an Experiment  

0. Connect the **photodiode** to the acquisition system and attach it to the **top-left corner** of the experiment laptop.  
1. Navigate to the corresponding experiment folder under `experiments/`.  
2. Double-click the executable file:  
   - **Category Localizer:** `CL_*.exe`  
   - **Language Mapping:** `LM_*.exe`  
   - **Motor Mapping:** `MM_*.exe`  
3. A command window will open. The experiment starts after a few seconds.  
4. Fill in the required fields in the pop-up window and press **OK**.  
5. Run the experiment until completion.  
6. Verify the behavioral output in the experiment’s `Results/` folder.  


## 3. How to Add or Replace Stimuli  

- Stimuli can be replaced **as long as file format and folder structure are preserved**.  
- Stimulus duration and timing are unaffected by file replacement.  
- Supported stimulus formats: `.wav`, `.txt`, `.png`.

**Example**  
To replace the German auditory stimulus `06_CHAT.wav`, create a new `.wav` file and save it using the **exact same filename** inside the corresponding language folder.


## 4. Folder Organization  

All experiments are organized under the `experiments/` directory and grouped by task and subtask.


## 5.Downloads (Windows)

Latest release of the FBM experiment suite include:

- Language Mapping  
- Audio Category Localizer  
- Visual Category Localizer  
- Motor Mapping  

You can find them at:
➡️ https://github.com/HumanNeuronLab/FBM_Experiments/releases/latest

Each executable must be placed inside the corresponding experiment folder for the tool to function correctly.
```
experiments/
├─ LanguageMapping/
│  ├─ FBM-LanguageMapping-Windows-v1.0.0.exe
│  └─ ...
├─ CategoryLocalizer/
│  ├─ Audio
|  |  ├─ FBM-CategoryLocalizerAudio-Windows-v1.0.0.exe
│  ├─ Visual
|  |  ├─ FBM-CategoryLocalizerVisual-Windows-v1.0.0.exe
│  └─ ...
├─ MotorMapping/
│  ├─ FBM-MotorMapping-Windows-v1.0.0.exe
│  └─ ...
```
