# 🎮 Stitch_Sync_Track — Hexmaze Rat Project

This folder integrates **multi-camera video synchronization**, **stitching**, and **automated rat tracking** for the **Hexmaze Rat** experiment.  
The goal is to produce a **fully synchronized behavioral dataset** — where every tracked rat position is precisely aligned to the neural recordings.

Importantly, **temporal synchronization** happens *before* stitching.  
Each camera video is aligned to the neural clock via **two-stage regression** (GPU→CPU and CPU→DIO), and these per-eye regressions are combined into a **single global timestamp series** that defines the true frame-by-frame timing of the final stitched video.

---

## 🧠 Conceptual Overview

The workflow combines behavioral videos and electrophysiology data through the following stages:

```
Multi-camera videos
→ Two-stage LED–DIO synchronization via ICA regression (per eye)
→ Averaged global timestamps (stitched_framewise_ts.csv)
→ Visual stitching of videos
→ Tracker applies timestamps to behavioral detections
→ Neural–behavioral dataset
```

---

## 🧬 Full Hex-Maze Video Processing Pipeline

This pipeline transforms raw multi-camera recordings of the **Hex-Maze** experiment into fully timestamped, analyzed videos that show the rat’s path across trials — all in true neural time.

It consists of three main stages:  
**1. Synchronization**, **2. Stitching**, and **3. Tracking**.

---

### 🕹️ Step 1 — Synchronization (`Video_LED_Sync_using_ICA.py`)

Each eye camera records independently, with its own clock that may drift slightly relative to the neural recording system.  
This script aligns all video frames to the **neural clock** using the LED–DIO system and builds the global timestamp mapping used later.

**How it works**
1. For each eye video, extracts a small LED region and applies **Independent Component Analysis (ICA)** to isolate the LED signal.  
2. Reads corresponding LED control pulses from the **neural DIO (.dat)** files, which store the ground-truth timing of LED blinks.  
3. Performs **two sequential linear regressions**:
   - **GPU → CPU regression:** corrects timestamp lag between frame capture (GPU) and metadata timestamp (CPU).  
     Implemented in `pred_cpu_ts_from_gpu_ts()`, this removes a consistent 10–30 ms delay caused by transfer latency inside the Raspberry Pi.  
   - **CPU → DIO regression:** maps corrected frame timestamps to neural DIO LED pulse times, aligning each frame to the neural clock.  
     Implemented in `pred_dio_ts_from_ica_ts_and_verify()`, it uses ICA-derived LED timestamps to compute per-eye neural-aligned frame times.  
4. **Averages** the per-eye regressions to produce a **single global framewise timestamp** shared by all cameras, ensuring every stitched frame has a unified neural-time reference.  
5. Outputs a single CSV (`stitched_framewise_ts.csv`) that defines the **corrected neural-aligned time** for every frame in the stitched video.

**Output**
- 🗂️ `stitched_framewise_ts.csv` — table indexed by frame number with the column "Corrected Time Stamp".  
  Each entry represents the **true neural-aligned timestamp** of that stitched frame, averaged across all eye regressions.

> ✅ This file is the core synchronization reference for all downstream steps.  
> ❌ It does *not* visually synchronize or merge the videos — it only defines time alignment.

---

### 🎥 Step 2 — Join Views (`join_views.py`)

The maze is recorded by multiple fixed cameras (typically 12).  
This script visually merges them into a single panoramic view for manual inspection and automated tracking.

**How it works**
1. Finds all individual eye videos in the target folder.  
2. Aligns their **first frame (frame 0)** to start simultaneously.  
3. Ends the output at the shortest input video duration.  
4. Optionally crops or flips videos to maintain consistent maze orientation.  
5. Uses **FFmpeg overlay filters** to tile the videos in a 2×6 grid and generate one stitched video.

**Output**
- 🎮 `stitched.mp4` — a single panoramic video combining all eye views.

> ⚠️ This stage performs **no temporal synchronization** — it simply places all camera videos side by side for visual convenience.  
> The precise neural timing is recovered later via the `stitched_framewise_ts.csv` file from Step 1.

---

### 🐀 Step 3 — Tracking (`TrackerYolov3-Colab.py`)

The tracker performs automatic rat detection and tracking on the **stitched video** using a trained **YOLOv3 ONNX** network.  
Each frame processed by the tracker is then assigned its **true neural timestamp** using the global timestamp mapping from synchronization.

**How it works**
1. Loads both `stitched.mp4` and `stitched_framewise_ts.csv`.  
2. Detects the rat’s head, body, and the experimenter using YOLOv3 inference.  
3. Tracks the rat’s movement across maze nodes (`node_list_new.csv`).  
4. For each processed frame, retrieves the corresponding "Corrected Time Stamp" from the CSV — the **global averaged timestamp** computed during synchronization.  
5. Logs detections and behavioral events using these neural-aligned timestamps.  
6. Annotates and saves the stitched video with trajectories, node IDs, and trial information.

**Outputs**
- 🐭 `<date>_Rat<ID>.mp4` — tracked video with path annotations.  
- 🖜 `log_<date>_Rat<ID>.log` — detailed frame-by-frame detections, each labeled with the neural-synchronized timestamp.  
- 📈 *(optional)* `<date>_Rat<ID>.txt` — session summary (nodes, durations, velocities, etc.).

---

### 🧩 Putting It All Together

| Stage | Inputs | Outputs | Purpose |
|:------|:--------|:---------|:---------|
| **1. Synchronization** | Eye videos + DIO signals | `stitched_framewise_ts.csv` | Compute neural-aligned timestamps for each frame (averaged across eyes) |
| **2. Join Views** | Eye videos | `stitched.mp4` | Merge all cameras into a visual grid (no timing correction) |
| **3. Tracker** | `stitched.mp4` + `stitched_framewise_ts.csv` | Tracked video + logs | Detect and log rat behavior in true neural time |

---

### 🧤 Key Insight

The **synchronization step** defines the true neural timeline using two-stage regression (GPU→CPU and CPU→DIO) and averaging across eyes.  
The **stitched video** is only a visual montage — it has no inherent timing correction.  
Finally, the **tracker** fuses both by applying the neural-aligned timestamps from `stitched_framewise_ts.csv` to every frame and event.

🟢 **In short:**  
- Synchronization = builds the global neural timeline.  
- Stitching = creates the visual grid.  
- Tracking = overlays rat detections and applies neural timestamps.

---

### 🧬 Final Outcome

At the end of the pipeline you obtain:
- A single **stitched video** showing all camera views.  
- A **tracked video** with the rat’s trajectory and trial annotations.  
- **Logs and summaries** where every event is timestamped in neural time, enabling precise behavioral–electrophysiological analysis.

---

## 📊 Output Files

| File | Description |
|------|--------------|
| `stitched.mp4` | Multi-camera panoramic video (visual only) |
| `stitched_framewise_ts.csv` | Global frame-to-neural timestamp table |
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
- **Olivier Peron** — GPU→CPU regression model and electrophysiology–video synchronization validation  
- **Özge Çekirge** — ICA-based LED–DIO synchronization and drift analysis  
- **Daniela Morales** — Colab and FFMPEG optimization  
- **Genzel Lab Team** — experimental data and conceptual design  

---
#### For a detailed explanation of the synchronization architecture and its implementation, see [SYNCHRONIZATION_DETAILS.md](SYNCHRONIZATION_DETAILS.md).
---

## 🟒 License

© **Genzel Lab** — for research use only.  

This folder combines three modules — **Synchronization**, **Stitching**, and **Tracking** — into a single executable workflow.  
Usage and Installation Manual:  
[Installation and Usage Manual – Dropbox Link](https://www.dropbox.com/scl/fi/wwph1cjct5o0m6cffelm3/Installation-and-Usage-Manual-for-HM-Stitch-Sync-Track.docx?rlkey=drsd7q3debt064n3khcz4tlji&st=qymj8ie4&dl=0)

---

📌 *Each frame in the stitched video inherits its timestamp from the averaged neural-aligned series (`stitched_framewise_ts.csv`), ensuring that all tracked rat positions are expressed in true experimental time.*

