# 🎬 Stitch_Sync_Track — Hexmaze Rat Project

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

## 📁 File Descriptions

| File | Function |
|------|-----------|
| **`join_views.py`** | Stitches 12-camera views into one panoramic video using OpenCV and FFMPEG. |
| **`Video_LED_Sync_using_ICA.py`** | Detects LED synchronization flashes via ICA decomposition to align ephys & video timestamps. |
| **`TrackerYolov3-Colab.py`** | Runs YOLOv3-based rat tracker (GPU-accelerated, Colab-ready). |
| **`run.sh`** | End-to-end automation script that performs stitching → synchronization → tracking. |
| **`requirements.txt`** | Lists dependencies: OpenCV, ONNX Runtime GPU, scikit-learn, matplotlib, pandas. |

---

## ⚙️ Detailed Pipeline

### 1. Video Stitching — `join_views.py`
Combines 12 raw camera videos into one stitched panoramic video.

**Input:** 12 individual `.mp4` files (Hexmaze cameras)  
**Output:** Single video file `stitched.mp4`  

**Command:**
```bash
python join_views.py --input ./videos/raw/ --output ./videos/stitched/stitched.mp4
```

**Notes:**
- Uses **OpenCV** and **FFMPEG** for parallelized stitching.  
- Supports GPU acceleration when available.  
- Output resolution and layout can be adjusted via the configuration section inside the script.

---

### 2. LED Synchronization — `Video_LED_Sync_using_ICA.py`
Synchronizes video frames with electrophysiology timestamps by detecting LED flashes.

**Input:**  
- Stitched video (`stitched.mp4`)  
- Corresponding ephys file (`session.rec`)

**Output:**  
- `sync_timestamps.csv` — alignment table between video and electrophysiology timestamps

**Command:**
```bash
python Video_LED_Sync_using_ICA.py --video ./videos/stitched/stitched.mp4 --ephys ./ephys/session.rec
```

**How it works:**
- Extracts video frame luminance signals.  
- Performs **Independent Component Analysis (ICA)** to isolate LED flash signals.  
- Matches detected LED peaks to electrophysiology timestamps.

---

### 3. Tracking — `TrackerYolov3-Colab.py`
Tracks rat position frame-by-frame using a YOLOv3-based detection model.

**Input:** Stitched and synchronized video (`stitched.mp4`)  
**Output:** Rat position and bounding box coordinates (`tracker_output.csv`)

**Command:**
```bash
python TrackerYolov3-Colab.py -i ./videos/stitched/stitched.mp4 -o ./output/
```

**Features:**
- GPU acceleration via **ONNX Runtime GPU**  
- Compatible with **Google Colab** and local CUDA systems  
- Generates detection logs and trajectory visualizations

---

### 4. Automated Workflow — `run.sh`
Executes the full pipeline from raw videos to tracker output.

**Command:**
```bash
bash run.sh ./videos/raw ./ephys/session.rec ./output/
```

**Steps performed:**
1. Run `join_views.py` for video stitching  
2. Run `Video_LED_Sync_using_ICA.py` for LED synchronization  
3. Run `TrackerYolov3-Colab.py` for tracking and output generation

---

## 📊 Output Files

| File | Description |
|------|--------------|
| `stitched.mp4` | Merged panoramic video from 12-camera input |
| `sync_timestamps.csv` | Mapping between video frames and ephys timestamps |
| `tracker_output.csv` | Rat trajectory and detection data |

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
- **Giulia Porro** — implemented the YOLOv3 tracker integration  
- **Param Rajpura** — GPU acceleration and synchronization improvements  
- **Daniela Morales** — optimized Colab and FFMPEG environments  
- **Genzel Lab Team** — experimental data and conceptual design  

---

## 🧾 License

© **Genzel Lab** — for research use only.  


This folder is the compilation of 3 projects to enable user to execute the workflow in single step.
Usage and Installation Document : https://www.dropbox.com/scl/fi/i59wadvyigozyv650okf3/Installation-and-Usage-Manual-for-HM-Stitch-Sync-Track.docx?rlkey=q5o6ppiv1xcbkq1w2v8oodvr1&dl=0

Tracker code now uses the output of the Synchronisation generated in outpath folder to write the sync timestamps in tracker log file.

The files are modified to run with relative folder paths without user intervention for each run. For debugging or visualisation, please refer to the original project folder for the python scripts or notebooks with similar names as in this project.
