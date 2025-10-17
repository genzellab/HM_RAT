# 🎮 Stitch_Sync_Track — Hexmaze Rat Project

This folder integrates multi-camera video stitching, synchronization with electrophysiological recordings, and automated rat tracking for the **Hexmaze Rat** experiment.  
The goal is to create a single, synchronized behavioral video that aligns precisely with the electrophysiological data, enabling combined neural–behavioral analyses.

---

## 🧠 Conceptual Overview

The workflow combines video and ephys data through the following stages:

```
Multi-camera videos → Stitched video → Synchronized frames via LED/ICA → Tracker → Position–event dataset
```

### Pipeline Summary

1. **Video Stitching** — merges multiple camera views into one panoramic video.  
2. **LED Synchronization** — detects LED flashes using ICA to align video and ephys timestamps.  
3. **Tracking** — extracts the rat’s position using a YOLOv3-based GPU-accelerated tracker.  
4. **Automated Workflow** — all steps can be executed sequentially via `run.sh`.

---

## 🧬 Hex-Maze Video Processing Pipeline – Full Description

This pipeline converts raw multi-camera recordings of the **Hex-Maze** experiment into fully synchronized, annotated, and analyzed videos that show the rat’s position across trials, aligned precisely with the neural data.  
It consists of three main stages: **Synchronization**, **Stitching**, and **Tracking**.

---

### 🕹️ Step 1 — Synchronization (`Video_LED_Sync_using_ICA.py`)

Each eye camera records independently, and their clocks may drift slightly relative to the neural recording system.  
The synchronization script aligns all video frames to the **neural clock** using the LED–DIO system.

**How it works**
1. Detects red and blue LED flashes in each eye video using **Independent Component Analysis (ICA)**.  
2. Reads the corresponding LED control pulses from the neural system’s **DIO .dat** files.  
3. Fits a **linear regression** between video and neural timestamps to correct offset and drift.  
4. Produces a frame-accurate mapping between each video frame and its true neural-aligned timestamp.

**Output**
- 🗂️ `stitched_framewise_ts.csv` — links each video frame index to a corrected neural-synchronized timestamp.  
  This file represents the **true temporal alignment** between the video and electrophysiological data and is the core reference for all subsequent steps.

---

### 🎥 Step 2 — Join Views (`join_views.py`)

The maze is recorded from multiple eye cameras (typically 12).  
This script visually combines all the videos into a single grid layout for easy viewing.

**How it works**
1. Finds all the eye videos in a folder.  
2. Aligns frame 0 across all videos (all start together).  
3. Ends at the shortest video’s length, ensuring matching time windows.  
4. Optionally crops or flips the views for consistent orientation.  
5. Creates a new video showing all camera views side-by-side.

**Output**
- 🎮️ `stitched.mp4` — a single multi-view video combining all camera angles.

> ⚠️ The stitching process does **not** use timestamps; it assumes videos are already roughly aligned.  
> Minor 1–2 frame offsets between cameras may remain but are corrected later through the synchronization file.

---

### 🐀 Step 3 — Tracker (`tracker.py`)

The tracker performs automated detection and tracking of the rat’s movements across the maze using a trained **YOLOv3 ONNX** network.  
It also associates every detected frame with its **true neural-synchronized timestamp**.

**How it works**
1. Loads the stitched video (`stitched.mp4`) and timestamp file (`stitched_framewise_ts.csv`).  
2. Detects rat head, rat body, and researcher positions frame by frame.  
3. Tracks the rat’s trajectory across maze nodes using `node_list_new.csv`.  
4. Logs every detection and event using corrected timestamps for full alignment with neural data.  
5. Annotates and saves the tracked video with colored paths, node labels, and trial information.

**Outputs**
- 🐭 `<date>_Rat<ID>.mp4` — tracked video with path annotations.  
- 📜 `log_<date>_Rat<ID>.log` — detailed synchronized frame-by-frame detections.  
- 📈 *(optional)* `<date>_Rat<ID>.txt` — summary of nodes, durations, and velocities.

---

### 🧠 Putting It All Together

| Stage | Inputs | Outputs | Purpose |
|:------|:--------|:---------|:---------|
| **1. Synchronization** | Eye videos + DIO signals | `stitched_framewise_ts.csv` | Align video timing to neural data |
| **2. Join Views** | Eye videos | `stitched.mp4` | Combine all camera views into one video |
| **3. Tracker** | `stitched.mp4` + `stitched_framewise_ts.csv` | Tracked video + logs (+ summary) | Detect and log rat behavior with precise neural timing |

---

### 🤎 Key Insight

The **stitched video** is only *visually* synchronized—it aligns all videos by frame index, not by corrected timestamps.  
The **Tracker** then uses `stitched_framewise_ts.csv` to assign each stitched frame its true neural-synchronized time, ensuring all behavioral logs and neural data are perfectly aligned.

🟢 **In short:**  
The *stitching* step creates a watchable multi-camera video,  
while the *Tracker* step restores and applies the true temporal correction using the synchronization data.

---

### 🧬 Final Outcome

At the end of the pipeline you obtain:
- A single **stitched video** showing all camera views.  
- A **tracked video** with the rat’s trajectory and trial information.  
- **Logs and summaries** where every behavioral event is precisely timestamped to match the neural recordings—ready for quantitative analysis.

---

## 📊 Output Files

| File | Description |
|------|--------------|
| `stitched.mp4` | Merged panoramic video from 12-camera input |
| `stitched_framewise_ts.csv` | Mapping between video frames and ephys timestamps |
| `log_<date>_Rat<ID>.log` | Frame-by-frame detections with synchronized timestamps |
| `<date>_Rat<ID>.mp4` | Tracked video with rat path and annotations |
| `<date>_Rat<ID>.txt` | Optional session summary (nodes, durations, velocities) |

---

## 📦 Dependencies

From `requirements.txt`:

```
opencv-python
matplotlib
onnxruntime-gpu
scikit-learn
pandas
```

Install via:
```bash
pip install -r requirements.txt
```

---

## 👥 Credits

Developed under the supervision of **[Dr. Adrián Alemán Zapata](https://github.com/Aleman-Z)**  

**Contributors:**
- **Giulia Porro** — YOLOv3 tracker integration  
- **Param Rajpura** — GPU acceleration and synchronization improvements  
- **Olivier Peron** — electrophysiology–video synchronization validation  
- **Özge Çekirge** — ICA-based synchronization analysis  
- **Daniela Morales** — Colab and FFMPEG optimization  
- **Genzel Lab Team** — experimental data and conceptual design  

---

## 🗾 License

© **Genzel Lab** — for research use only.  

This folder is the compilation of 3 projects to enable users to execute the workflow in a single step.  
Usage and Installation Document:  
[Installation and Usage Manual – Dropbox Link](https://www.dropbox.com/scl/fi/i59wadvyigozyv650okf3/Installation-and-Usage-Manual-for-HM-Stitch-Sync-Track.docx?rlkey=q5o6ppiv1xcbkq1w2v8oodvr1&dl=0)

---

📌 *The tracker now uses the output of the Synchronization module to write neural-synchronized timestamps directly into the log files, ensuring precise temporal alignment between behavior and neural events.*
