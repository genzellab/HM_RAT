# 🧠 Hexmaze Synchronization Technical Notes  
### Detailed Explanation of the Synchronization Framework  
*(based on the analyses and implementations by Olivier Perron & Özge Çekirge, 2023–2024)*

The current **Hexmaze synchronization pipeline** builds on the foundational work of **Olivier Perron** and **Özge Çekirge**, who analyzed the multi-clock architecture of the Hexmaze video–neural recording setup.  
Their work characterized timing drifts between video (Raspberry Pi) and neural (SpikeGadget) systems, directly informing the design of the automated synchronization procedure implemented in `Video_LED_Sync_using_ICA.py`.

---

## 🕒 1. Multi-Clock Recording System

The Hexmaze experiment uses several asynchronous clocks, each introducing measurable timing drift or jitter:

| Device | Clock | Function | Drift Behavior |
|:--------|:------|:----------|:----------------|
| **SpikeGadget** | SG-clock | Electrophysiology acquisition (30 kHz) + DIO LED pulses | Very stable; defines the neural reference |
| **Raspberry Pi GPU** | GPU-clock | Actual frame capture timing | Slight negative drift (frames slightly faster) |
| **Raspberry Pi CPU** | CPU-clock | Metadata timestamps (`callback_clock_ts`) | Adds random jitter + communication delay |
| **Beholder PC** | Sys-clock (NTP-synced) | Launch/control computer | Only coarse alignment; not frame-accurate |

Although the Beholder triggers both the SpikeGadget and the Raspberry Pis, each subsystem starts independently, introducing small offsets that must be corrected computationally.

---

## 💻 2. Frame Acquisition and Communication Delays

Olivier Perron showed that **CPU timestamps systematically lag GPU timestamps** due to frame transfer delays between the Raspberry Pi’s **GPU (VideoCore IV)** and **CPU (ARM Cortex)**.  
He modeled this lag as a near-linear function — a finding that led directly to the GPU→CPU correction now implemented in the pipeline.

In the current script, this correction is handled by:

```python
pred_cpu_ts_from_gpu_ts(gpu, cpu)
```

This function:
1. Fits a **linear regression** (`LinearRegression().fit(gpu, cpu)`) to model the delay between GPU and CPU timestamps.  
2. Computes a **mean offset** from the first 1000 samples.  
3. Subtracts the offset to generate a **corrected CPU timestamp array**, which reflects the actual frame capture time.

The correction is applied within:

```python
process_video_with_metadata()
```

Each video’s `.meta` file contains the GPU and CPU timestamps (`callback_gpu_ts`, `callback_clock_ts`).  
These are processed as:

```python
corr_cpu_ts = pred_cpu_ts_from_gpu_ts(ts_data['callback_gpu_ts'],
                                      ts_data['callback_clock_ts'])
df['extracted_seconds_timestamp'] = pd.to_datetime(corr_cpu_ts, unit='s', utc=True)
```

This converts GPU→CPU–corrected timestamps into per-frame acquisition times in **true capture time**, effectively removing communication delay and drift.  
*(See lines ~380–450 in `Video_LED_Sync_using_ICA.py`.)*

---

## 💡 3. LED–DIO Synchronization via ICA Regression

Both **Özge Çekirge** and **Olivier Perron** demonstrated that the **LED flashes controlled by SpikeGadget DIO** provide a reliable link between neural and video time domains.  
This principle evolved into the modern, per-eye ICA-based synchronization implemented in the same script.

Each eye video is processed individually via:

```python
process_video_with_metadata()
```

This function:
1. Reads the eye video and crops the LED region (from `.led_crop` coordinates).  
2. Runs **FastICA** on 16×16 pixel LED crops:
   ```python
   ica = FastICA(n_components=3, random_state=0)
   demixed = ica.fit_transform(X)
   ```
3. Calls:
   ```python
   process_ica_signals(demixed, mix_weights, df['extracted_seconds_timestamp'])
   ```
   to extract **red and blue LED components** via K-Means clustering and frequency filtering, identifying which component corresponds to each LED color.  
4. Outputs two DataFrames (`df_red_out`, `df_blue_out`) containing LED intensities and corrected timestamps — one per eye.

Next, the DIO signals from SpikeGadget are read using:

```python
extract_dio_com(dio_file_path_dict, sampling_freq)
```

This computes the **center-of-mass (COM)** timestamps for red and blue LED pulses.  
These are then regressed against ICA timestamps through:

```python
pred_dio_ts_from_ica_ts_and_verify()
```

which fits a **linear model between ICA → DIO** to map video-derived timestamps to the neural clock.  
This produces per-eye neural-aligned timestamps.

Finally, all per-eye results are **averaged** to form a single, global neural timestamp array (`avg_ts_per_frame`), saved as:

```
stitched_framewise_ts.csv
```

This ensures that, although each eye captures slightly different frames (1–2 frame shutter offsets), all stitched frames share a unified neural-synchronized timeline.  
*(See lines ~900–1100 in `Video_LED_Sync_using_ICA.py`.)*

---

## 🧲 4. From Per-Eye Regressions to a Global Neural Timestamp

Because each Raspberry Pi operates on its own internal clock, small inter-eye offsets remain even after LED-based correction.  
To unify timing:

- Each eye is first synchronized to the DIO via ICA→DIO regression.  
- The resulting timestamps are **averaged across eyes** to produce a single, global time series.  
- The series is **truncated** to match the shortest eye recording.  

The output file, `stitched_framewise_ts.csv`, provides the **neural-aligned timestamp** for every frame in the stitched video.

---

## 🎥 5. Independent Stitching and Tracking

Hardware-level camera triggers are not implemented, so residual 1–2 frame misalignments persist across eyes.  
To avoid compounding errors, the workflow keeps stitching and synchronization **independent**:

- **`join_views.py`** aligns all eye videos visually (starting from frame 0, truncated to the shortest video) to produce the multi-view composite `stitched.mp4`.  
- **`TrackerYolov3-Colab.py`** then uses the synchronized timestamps from `stitched_framewise_ts.csv` to map each stitched frame to its true neural-aligned time.

This modular design ensures visual inspection and neural-aligned analysis remain consistent but logically independent.

---

## ✅ Summary

- **Olivier Perron** quantified GPU–CPU latency and implemented the correction now used in `pred_cpu_ts_from_gpu_ts()`.  
- **Özge Çekirge** formalized the two-stage regression (GPU→CPU, CPU→SG via LED–DIO) and demonstrated per-eye ICA synchronization.  
- The **current pipeline** automates these procedures, averages per-eye results into a global neural timeline, and integrates them with the stitching and tracking modules.

The result is a **robust, reproducible synchronization framework** aligning behavioral and neural data with sub-frame temporal precision.

---

