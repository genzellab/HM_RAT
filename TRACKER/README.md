## HM TRACKER 
# 🎯 Hexmaze Rat — TRACKER Module  

GPU-accelerated rat tracking system based on **YOLOv3** for multi-camera behavioral recordings in the Hexmaze.  
This module extracts rat trajectories from stitched videos and synchronizes them with electrophysiological data.

---

## 👥 Credits

Developed under the supervision of **[Dr. Adrián Alemán Zapata](https://github.com/Aleman-Z)**.  

**Contributors:**  
- **Giulia Porro** — implemented the original YOLOv3 tracker and Colab version  
- **Param Rajpura** — implemented GPU acceleration and optimized synchronization with electrophysiological data  
- **Daniela Morales** — supported GPU optimization and computational setup  
- **Genzel Lab Team** — integration and validation with multi-camera recordings  

---

## ⚙️ Overview

This module detects and tracks rats across videos recorded from the **Hexmaze setup (12 cameras)**.  
It uses a YOLOv3-based detection model to extract trajectories, running efficiently on both **local GPU machines** and **Google Colab**.

The tracking pipeline includes:
1. **Model initialization** with pre-trained YOLOv3 weights (.onnx or .rar)
2. **GPU-based inference** for rapid frame-by-frame detection
3. **Trajectory logging** into `.csv` and `.txt` outputs
4. **Synchronization** with electrophysiological timestamps for joint behavioral–neural analysis

---

## 💻 Installation & Dependencies

### 1. Environment Requirements
- **Python ≥ 3.8**  
- **CUDA ≥ 11.6**  
- **cuDNN ≥ 8.5.0.96**  
- **ONNX Runtime GPU (tested with v1.8.1)**  
- **TensorFlow GPU (optional for hardware validation)**  

### 2. Python Packages
```bash
pip install onnxruntime-gpu==1.8.1 tensorflow pyunpack opencv-python tqdm
```

---

## 🚀 Usage

### 🔹 Local GPU Execution

```bash
python TRACKER_GPU.py -i /path/to/video/stitched.mp4 -o /path/to/output/folder
```

**Arguments:**
- `-i` : path to input stitched video (e.g., from `video_stitching/`)  
- `-o` : output directory containing `/logs` and `/videos` subfolders  

Example:
```bash
python TRACKER_GPU.py -i ./stitched_videos/Rat5_20210614_presleep.mp4 -o ./tracker_output/
```

---

### 🔹 Running on Google Colab

You can also execute the tracking pipeline on **Google Colab** using the provided notebooks:
- **`Tracker_Colab_2_0.ipynb`** — GPU-based inference  
- **`TRACKER GPU.ipynb`** — interactive version for testing and visualization  

Steps:
1. Mount your Google Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
2. Clone the repository or upload the tracker folder.
3. Extract model weights (`ModelWeights.rar`):
   ```python
   from pyunpack import Archive
   Archive('/content/drive/MyDrive/TrackerTools/ModelWeights.rar').extractall('/content/tracker/')
   ```
4. Run the tracker:
   ```bash
   !python /content/tracker/TrackerYolov3-Colab.py -i /content/tracker/stitched.mp4 -o /content/tracker/
   ```

Output trajectories and logs are saved under:
```
/videos  → processed videos with detections  
/logs    → text and CSV files with position and detection metadata
```

---

## 🧠 Synchronization

After tracking, the trajectories can be synchronized with electrophysiology recordings using the **`SYNCHRONIZATION/`** and **`Stitch_Sync_Track/`** modules.  
The synchronization aligns behavioral timestamps with LFP or spike data exported from Trodes.

---

## 🧾 Notes

- For best GPU performance, ensure ONNX Runtime GPU and CUDA/cuDNN versions are correctly matched.  
- Tested configurations:
  - **ONNX Runtime GPU**: 1.8.1  
  - **CUDA**: 11.6  
  - **cuDNN**: 8.5.0.96  
- Supported input: stitched videos in `.mp4` format (typically 12-camera composites).  

---

## 📂 Folder Structure
```
TRACKER/
│
├── TRACKER_GPU.py                 # GPU-based tracking script (local execution)
├── TRACKER GPU.ipynb              # Interactive tracking notebook
├── Tracker_Colab_2_0.ipynb        # Colab version for large-scale tracking
├── ModelWeights.rar               # YOLOv3 model weights
├── logs/                          # Tracking logs and outputs
└── README.md                      # This file
```

---

## 🧩 Integration

This module is part of the full **HM_RAT** pipeline:
- [`video_stitching/`](../video_stitching) → merges multi-camera recordings  
- [`SYNCHRONIZATION/`](../SYNCHRONIZATION) → aligns tracking with electrophysiology  
- [`LFP_event_detection/`](../LFP_event_detection) → detects ripples, spindles, delta events

---

## 📜 License  
© **Genzel Lab** — for research use only.  
Please cite relevant publications and acknowledge **[Dr. Adrián Alemán Zapata](https://github.com/Aleman-Z)** for supervision.


The versions used by Giulia were onnruntime-gpu-1.8.1 and the latest versions of CUDA and cuDNN.
In the most recent issue about onnx predictions they were using CUDA 11.6 and cnDNN 8.5.0.96
