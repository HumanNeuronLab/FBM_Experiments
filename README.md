# HNL_Experiments  
Experiments for the Human Neuron Lab (HNL)

**Contact**  
Pierre Megevand – pierre.megevand@unige.ch  
Lora Fanda – lorafanda7@gmail.com  

---

## 1. Demo   

### Full Walkthrough Video  
[![Watch the experiment walkthrough](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)  
*(Replace `VIDEO_ID` with your own link)*  

---

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

---

## 3. How to Add or Replace Stimuli  

- Stimuli can be replaced **as long as file format and folder structure are preserved**.  
- Stimulus duration and timing are unaffected by file replacement.  
- Supported stimulus formats: `.wav`, `.txt`, `.png`.

**Example**  
To replace the German auditory stimulus `06_CHAT.wav`, create a new `.wav` file and save it using the **exact same filename** inside the corresponding language folder.

---

## 4. Folder Organization  

All experiments are organized under the `experiments/` directory and grouped by task and subtask.

---

### 4.1 Language Mapping  

