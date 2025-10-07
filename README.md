# 🧠 HM_RAT — Hexmaze Rat Project  
Repository for the **Hexmaze Rat** electrophysiology and behavioral data analysis pipeline.

This repository contains scripts and utilities for synchronizing electrophysiological recordings with behavior, spike sorting, downsampling, event detection, and event characterization.  
It was developed within the **Genzel Lab**, to process and analyze LFP and spike data recorded from rats navigating the Hexmaze.

---

## 👥 Credits & Supervision

This repository was developed under the **main supervision of Dr. Adrián Alemán Zapata**, who designed the data analysis framework, integrated the preprocessing and synchronization pipelines, and organized the repository.

**Contributors:**
- **Dr. Adrián Alemán Zapata** — main supervision, data integration, and repository organization  
- **Emanuele Ciardo** — LFP preprocessing and event detection pipeline  
- **Sara Rostami** — event characteristics analysis and visualization  
- **Param Rajpura** — updated the tracker to use GPU acceleration and improved ephys–tracker synchronization  
- **Daniela Morales** — assisted with GPU acceleration and computational optimization  
- **Kayvan Combadiere** — contributed to the spike sorting pipeline structure and implementation  
- **Anna Gondret** — tested and validated the spike sorting pipeline on extended datasets  
- Additional contributions from members of the **Genzel Lab**

---

## ⚙️ Dependencies  
*(To be added — e.g., Python, MATLAB, Mountainsort, Trodes, etc.)*

---

## 🔄 Conversion from `.rec` to `.mda`

Use `trodesexport` to convert `.rec` recordings into `.mda` format compatible with the Mountainsort spike sorting pipeline:

```bash
./trodesexport -mountainsort -rec /mnt/genzel/Rat/HM/Rat_HM_Ephys/Rat_HM_Ephys_Rat5_406576/Rat_HM_Ephys_Rat5_406576_20210614/Rat_Hm_Ephys_Rat5_406576_20210614_presleep/Rat_Hm_Ephys_Rat5_406576_20210614_presleep.rec -sortingmode 1
./trodesexport -mountainsort -rec
```

---

## 🧩 Downsampling `.mda` Files

The script `DownsamplingMDAfile` performs temporal downsampling of `.mda` electrophysiology files for efficient analysis.

### Installation (Python packages)
```bash
pip install numpy pandas scipy
```

---

## 📊 LFP Analysis — *Emanuele Ciardo*

### Data Preprocessing  
Add the `mdaio` library to the Python path before running scripts.

- **`main.m`** — Takes a downsampled `.mda` file as input, loads the corresponding sleep scoring file (“states”), and selects NREM portions for event analysis.

### Independent Component Selection  
- **`main_ica.m`** — Receives output from `main.m` and identifies independent components to be removed.  
  Also allows manual selection of cortical (PFC) and hippocampal (HPC) channels.

### Event Detection  
- **`main_event.m`** — Detects neural events (ripples, spindles, delta waves) after removing movement artifacts.  
  - Removes artifacts via amplitude- and derivative-based thresholds.  
  - Segments data into NREM bouts.  
  - Supports interactive threshold tuning and visual inspection.

### Event Analysis  
- **`main_analysis.m`** — Performs event counting, co-occurrence analysis, and basic sequence analysis.

---

## 🧠 Event Characteristics — *Sara Rostami*

### Data Pooling  
Combines preprocessed data across study days and rats for feature extraction.

- **`pooling_data.m`** — Merges data from multiple rats (e.g., Rat 1, 2, 4, 7, 8) into `.mat` files for *pre/post-condition* analyses (e.g., `postsleep_homecage.mat`).

### Feature Extraction and Modeling  
- **`making_event_characteristics_file.m`** — Converts extracted event features to `.csv` format.  
- **`violin_plots_ripple_events.ipynb`** — Generates violin plots for ripple event feature visualization.  
- **`model&test.ipynb`** — Exploratory and predictive analysis using models (Decision Tree, Random Forest, SGBDT, KNN).  
- **`event_characteristics_plots.ipynb`** — Visualizes and compares event features across sleep sessions post-learning.

📄 Reports and plots:
- [Event Report 1](https://docs.google.com/document/d/1gvLbRoj9SJaflvzC6W12gw_GmWY8hxWR6e2fygoqZa0/edit#)  
- [Event Report 2](https://docs.google.com/document/d/1oe6Gip6X3RxoDDiwbFWX5XeOop_DhHowTUK5JEEMFok/edit#heading=h.2gazcsgmxkub)

---

## 📂 Repository Structure
```
HM_RAT/
│
├── LFP_event_detection/           # Event detection scripts (ripples, spindles, delta)
├── SYNCHRONIZATION/               # Trodes and tracker synchronization utilities
├── Spikesorting_and_preprocessing/# Spike sorting and preprocessing (Mountainsort)
├── Stitch_Sync_Track/             # Behavioral tracking and stitching
├── TRACKER/                       # GPU-accelerated tracking utilities
├── downsampling/                  # Signal downsampling scripts
├── event_characteristics/         # Feature extraction and modeling
├── video_stitching/               # Video alignment and reconstruction
└── README.md
```

---

## 🧾 License  
© **Genzel Lab** — for research use only.  
Please cite relevant publications and acknowledge **Dr. Adrián Alemán Zapata** for primary supervision when using this repository.
