# 🎮 Stitch_Sync_Track — Hexmaze Rat Project

This folder integrates multi-camera video stitching, synchronization with electrophysiological recordings, and automated rat tracking for the **Hexmaze Rat** experiment.  
The goal is to produce a **fully synchronized behavioral dataset**—where the tracked rat trajectories and events are precisely aligned with the electrophysiological recordings—enabling joint neural–behavioral analyses.

While the intermediate stitched video provides a visually combined multi-camera view, the *true temporal synchronization* is achieved through the alignment data computed in the **Synchronization** stage and later applied during **Tracking**.

---

## 🧠 Conceptual Overview

The workflow combines video and ephys data through the following stages:

```
Multi-camera videos → Stitched video → Neural synchronization via LED/ICA + DIO regression → Tracker → Position–event dataset
```

### Pipeline Summary

1. **Video Stitching** — merges multiple camera views into one panoramic video.  
2. **LED–DIO Synchronization** — aligns all video frames to the neural clock using LED detection and regression-based correction.  
3. **Tracking** — extracts and timestamps the rat’s position using a YOLOv3-based GPU-accelerated tracker.  
4. **Automated Workflow** — all steps can be executed sequentially via `run.sh`.

---

## 🧬 Hex-Maze Video Processing Pipeline – Full Description

This pipeline converts raw multi-camera recordings of the **Hex-Maze** experiment into fully synchronized, annotated, and analyzed videos that show the rat’s position across trials, aligned precisely with the neural data.  
It consists of three main stages: **Synchronization**, **Stitching**, and **Tracking**.

---

### 🎡️ Step 1 — Synchronization (`Video_LED_Sync_using_ICA.py`)

Each eye camera records independently, and their clocks may drift slightly relative to the neural recording system.  
The synchronization script aligns all video frames to the **neural clock** using the LED–DIO system.

**How it works**
1. For each eye video, it extracts a small LED crop and applies **Independent Component Analysis (ICA)** to separate red and blue LED signals.  
2. It reads the corresponding LED control pulses from the **neural DIO (.dat)** files, which encode the ground-truth timing of the LED blinks.  
3. It builds a **linear regression model** that maps each video’s LED timestamps to the DIO (neural) timestamps—correcting both offset and clock drift.  
4. For all eyes, it computes an **average per-frame timestamp** (since each camera is within ~1–2 frames of the others).  
5. It applies the regression model to this averaged timeline, converting every video frame into its **true neural-aligned time**.

**Output**
- 🗂️ `stitched_framewise_ts.csv` — a table linking each frame index in the stitched video to its corrected, neural-synchronized timestamp.  
  This file encodes the *true temporal alignment* between the behavioral videos and the electrophysiological data and is used directly by the tracker.

**In short:**  
The synchronization step translates frame indices into real neural time using ICA-based LED detection, DIO alignment, and linear regression—producing the master timestamp file used downstream.

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

> ⚠️ The stitching process does **not** use timestamps; it assumes all videos are approximately aligned.  
> Minor 1–2 frame offsets between cameras remain but are corrected downstream using the synchronization file.

---

### 🐀 Step 3 — Tracker (`tracker.py`)

The tracker performs automated detection and tracking of the rat’s movements across the maze using a trained **YOLOv3 ONNX** network.  
It also associates every detected frame with its **true neural-synchronized timestamp**.

**How it works**
1. Loads the stitched video (`stitched.mp4`) and the synchronization table (`stitched_framewise_ts.csv`).  
2. Detects rat head, rat body, and researcher positions frame by frame.  
3. Tracks the rat’s trajectory across maze nodes using `node_list_new.csv`.  
4. For each frame, looks up the **neural-aligned timestamp** from the CSV to tag detections in neural time.  
5. Logs every detection and event using corrected timestamps for full alignment with electrophysiology.  
6. Annotates and saves the tracked video with colored paths, node labels, and trial information.

**Outputs**
- 🐭 `<date>_Rat<ID>.mp4` — tracked video with path annotations.  
- 🔜 `log_<date>_Rat<ID>.log` — detailed frame-by-frame detections (including neural-synchronized timestamps).  
- 📊 *(optional)* `<date>_Rat<ID>.txt` — session summary (nodes, durations, velocities).

---

### 🧠 Putting It All Together

| Stage | Inputs | Outputs | Purpose |
|:------|:--------|:---------|:---------|
| **1. Synchronization** | Eye videos + DIO signals | `stitched_framewise_ts.csv` | Compute neural-aligned timestamps per frame |
| **2. Join Views** | Eye videos | `stitched.mp4` | Create a multi-camera visual representation |
| **3. Tracker** | `stitched.mp4` + `stitched_framewise_ts.csv` | Tracked video + logs (+ summary) | Detect and log rat behavior with precise neural timing |

---

### 🦿 Key Insight

The **stitched video** is only *visually aligned* (frame-based).  
The **true synchronization** is numerical and comes from `stitched_framewise_ts.csv`, which maps every frame to its corresponding neural time.  

When the tracker runs, it **reads that timestamp for each frame** to recover the real experimental timing—effectively fusing behavioral and neural data.

🟢 **In short:**  
The *Stitching* step creates an easy-to-watch panoramic video,  
while the *Synchronization* and *Tracking* steps together restore and apply the precise temporal alignment to produce a truly synchronized behavioral dataset.

---

### 🤜 Final Outcome

At the end of the pipeline you obtain:
- A single **stitched video** showing all camera views.  
- A **tracked video** with the rat’s trajectory and trial information.  
- **Logs and summaries** where every behavioral event is precisely timestamped to match the neural recordings—ready for quantitative analysis.

---

## 📊 Output Files

| File | Description |
|------|--------------|
| `stitched.mp4` | Merged panoramic video from 12-camera input |
| `stitched_framewise_ts.csv` | Mapping between each stitched frame and neural-aligned time |
| `log_<date>_Rat<ID>.log` | Frame-by-frame detections with synchronized timestamps |
| `<date>_Rat<ID>.mp4` | Tracked video with annotated rat path |
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
- **Param Rajpura** — GPU acceleration and synchronization implementation (ICA–DIO regression)  
- **Olivier Peron** — electrophysiology–video synchronization validation  
- **Özge Çekirge** — ICA-based synchronization analysis  
- **Daniela Morales** — Colab and FFMPEG optimization  
- **Genzel Lab Team** — experimental data and conceptual design  

---

## 🗾 License

© **Genzel Lab** — for research use only.  

This folder combines three modules (Stitching, Synchronization, and Tracking) into a single executable workflow.  
Usage and Installation Manual:  
[Installation and Usage Manual – Dropbox Link](https://www.dropbox.com/scl/fi/i59wadvyigozyv650okf3/Installation-and-Usage-Manual-for-HM-Stitch-Sync-Track.docx?rlkey=q5o6ppiv1xcbkq1w2v8oodvr1&dl=0)

---

📌 *The tracker directly uses the synchronized timestamps (`stitched_framewise_ts.csv`) to log rat positions in neural time, ensuring perfect alignment between behavioral and electrophysiological events.*
