# 🧠 HM_RAT — Hexmaze Rat Project  
Repository for the **Hexmaze Rat** electrophysiology and behavioral data analysis pipeline.

This repository contains scripts and utilities for synchronizing electrophysiological recordings with behavior, spike sorting, downsampling, event detection, and event characterization.  
It was developed within the **Genzel Lab**, to process and analyze LFP and spike data recorded from rats navigating the Hexmaze.

---

## 👥 Credits & Supervision

This repository was developed under the **main supervision of [Dr. Adrián Alemán Zapata](https://github.com/Aleman-Z)**, who designed the data analysis framework, integrated the preprocessing and synchronization pipelines, and organized the repository.

**Contributors:**
- **[Dr. Adrián Alemán Zapata](https://github.com/Aleman-Z)** — main supervision, data integration, and repository organization  
- **Giulia Porro** — implemented the original YOLOv3 tracker and Colab version for behavioral analysis
- **Olivier Peron** — contributed to electrophysiology–video synchronization and testing of LED-based alignment
- **Özge Çekirge** — assisted with ICA-based video–ephys synchronization and data validation  
- **Param Rajpura** — updated the tracker to use GPU acceleration and improved ephys–tracker synchronization  
- **Kayvan Combadiere** — contributed to the spike sorting pipeline structure and implementation   
- **Emanuele Ciardo** — LFP preprocessing and event detection pipeline  
- **Sara Rostami** — event characteristics analysis and visualization  
- **Daniela Morales** — assisted with GPU acceleration and computational optimization  
- **Anna Gondret** — tested and validated the spike sorting pipeline on extended datasets  
- Additional contributions from members of the **Genzel Lab**

---

## 🎥 Behavioral Tracking, Synchronization & Stitching

A key part of the Hexmaze Rat project involves **tracking animal behavior** across 12 synchronized camera views and aligning these behavioral datasets with **electrophysiological recordings (LFPs and spikes)**.

### 🧩 Stitching, Synchronization, and Tracking Pipeline
Folder: [`Stitch_Sync_Track/`](./Stitch_Sync_Track)

This integrated pipeline allows the user to:
- **Synchronize** electrophysiology (Trodes) and video data.  
- **Stitch** multiple camera feeds into a single continuous video using FFMPEG.  
- **Track** animal movement automatically with GPU acceleration (YOLOv3-based tracker).  

It combines three core modules:
- **Video stitching** (`video_stitching/`) — merges the 12 camera “Hexmaze eyes” into one video.  
- **Tracker** (`TRACKER/`) — GPU-accelerated YOLOv3 tracking pipeline, compatible with both Windows and Colab environments.  
- **Synchronization** — aligns electrophysiology timestamps with tracker outputs, generating synchronized position–event datasets.

The pipeline can be executed as a single automated workflow using the shell script `run.sh`.  
A detailed [installation and usage manual](https://www.dropbox.com/scl/fi/j59wadyvigqzyv650okf3/Installation-and-Usage-Manual-for-HM-Stitch-Sync-Track.docx?rlkey=q5o6ppiv1xcbkq1w2v8oodvr18dl=0) is available.

---

### 🎬 Video Stitching
Folder: [`video_stitching/`](./video_stitching)

Scripts to merge the 12 Hexmaze camera views into one video using **FFMPEG**.

- **`stitch.py`** — main stitching script for Windows.  
- **`join_views.py`** — Linux version (supports GPU acceleration).  
- **`Stitched_overlay.py`** — improves visual continuity and reduces abrupt cropping.  
- Installation instructions available in *Hexmaze stitcher installation.docx*.

---

### 🧭 Tracker (GPU-Accelerated)
Folder: [`TRACKER/`](./TRACKER)

Implements YOLOv3-based tracking of the rat’s position using GPU acceleration.  
Compatible with CUDA and cuDNN, with configurations for both Colab and local systems.

- **`TRACKER_GPU.py`** / **`TRACKER GPU.ipynb`** — main tracking scripts.  
- **`Tracker_Colab_2_0.ipynb`** — Colab-optimized version for large-batch tracking.  
- Supports ONNX runtime GPU (tested with CUDA 11.6 and cuDNN 8.5.0.96).  

GPU optimization credits: *Giulia Porro*, *Param Rajpura*, and *Daniela Morales.*

---

## ⚙️ Dependencies  
*(To be added — e.g., Python, MATLAB, Mountainsort, Trodes, FFMPEG, YOLOv3)*

---

## 🔄 Conversion from `.rec` to `.mda`

Use `trodesexport` to convert `.rec` recordings into `.mda` format compatible with the Mountainsort spike sorting pipeline:

```bash
./trodesexport -mountainsort -rec /mnt/genzel/Rat/HM/Rat_HM_Ephys/Rat_HM_Ephys_Rat5_406576/Rat_HM_Ephys_Rat5_406576_20210614/Rat_Hm_Ephys_Rat5_406576_20210614_presleep/Rat_Hm_Ephys_Rat5_406576_20210614_presleep.rec -sortingmode 1
./trodesexport -mountainsort -rec
```

---

## 🧠 LFP and Event Analyses

### LFP Analysis — *Emanuele Ciardo*  
Includes preprocessing, ICA-based artifact removal, and event detection (ripples, spindles, delta).

### Event Characteristics — *Sara Rostami*  
Aggregates and compares features across study days and animals, visualizing distributions and relationships through violin plots, correlation matrices, and predictive models.

📄 Reports and plots:
- [Event Report 1](https://docs.google.com/document/d/1gvLbRoj9SJaflvzC6W12gw_GmWY8hxWR6e2fygoqZa0/edit#)  
- [Event Report 2](https://docs.google.com/document/d/1oe6Gip6X3RxoDDiwbFWX5XeOop_DhHowTUK5JEEMFok/edit#heading=h.2gazcsgmxkub)

---

## 📂 Repository Structure
```
HM_RAT/
│
├── LFP_event_detection/            # Event detection scripts (ripples, spindles, delta)
├── SYNCHRONIZATION/                # Trodes and tracker synchronization utilities
├── Spikesorting_and_preprocessing/ # Spike sorting and preprocessing (Mountainsort)
├── Stitch_Sync_Track/              # Integrated stitching, synchronization, and tracking pipeline
├── TRACKER/                        # GPU-accelerated tracking utilities (YOLOv3)
├── video_stitching/                # Video merging and overlay correction
├── downsampling/                   # Signal downsampling scripts
├── event_characteristics/          # Feature extraction and modeling
└── README.md
```

---

## 🧾 License  
© **Genzel Lab** — for research use only.  
