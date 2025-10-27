# 🧠 Hexmaze Synchronization Technical Notes  
### Detailed Explanation of the Synchronization Framework  
*(based on the analyses and implementations by Olivier Perron & Özge Çekirge, 2023–2024)*

The **Hexmaze synchronization pipeline** is built on foundational work by **Olivier Perron** and **Özge Çekirge**, who investigated the timing relationships between the neural (SpikeGadget) system and the Raspberry Pi camera network. Their analyses established how GPU, CPU, and DIO timestamps drift over time and how to mathematically align them. These findings directly informed the two-stage regression and averaging system implemented in `Video_LED_Sync_using_ICA.py`.

---

## ⏱️ 1. Multi-Clock Recording System

Each Raspberry Pi and the SpikeGadget system have independent clocks that drift slightly over time. The key systems involved are:

| Device | Clock | Function | Drift Behavior |
|:--------|:------|:----------|:----------------|
| **SpikeGadget** | SG-clock | Electrophysiology acquisition (30 kHz) + DIO LED pulses | Very stable; defines the neural reference |
| **Raspberry Pi GPU** | GPU-clock | Actual frame capture time | Slight negative drift (frames slightly faster) |
| **Raspberry Pi CPU** | CPU-clock | Metadata timestamps (`callback_clock_ts`) | Adds jitter and delay relative to GPU |
| **Beholder PC** | Sys-clock (NTP) | Launch control computer | Coarse sync only, not used for frame-level correction |

Thus, while Beholder triggers all devices nominally at the same time, each Raspberry Pi runs freely afterward, causing small inter-eye offsets.  These offsets are corrected computationally.

---

## 💻 2. GPU → CPU Timestamp Correction (Olivier Perron’s Model)

The first stage of regression corrects the lag between when a frame is **actually captured** (GPU time) and when the CPU records that frame (CPU time). This compensates for transfer latency between the Raspberry Pi’s GPU and CPU subsystems.

**Relevant code section:** ~lines **370–450** in `Video_LED_Sync_using_ICA.py`

```python
def pred_cpu_ts_from_gpu_ts(gpu, cpu):
    model = LinearRegression().fit(gpu.reshape(-1, 1), cpu)
    fitted = model.predict(gpu.reshape(-1, 1))
    offset = np.mean(cpu[:1000] - gpu[:1000])   # mean lag correction
    corrected_cpu = cpu - offset
    return corrected_cpu, model
```

Used inside:

```python
def process_video_with_metadata(...):
    corr_cpu_ts, reg = pred_cpu_ts_from_gpu_ts(
        ts_data['callback_gpu_ts'],
        ts_data['callback_clock_ts']
    )
    df['extracted_seconds_timestamp'] = pd.to_datetime(corr_cpu_ts, unit='s', utc=True)
```

✅ **Explanation:**  
This regression estimates and removes the ~10–30 ms lag between GPU and CPU clocks. The mean offset across the first 1000 frames is subtracted to get corrected per-frame timestamps, representing **true frame capture times**.

This correction is critical for the subsequent ICA–DIO regression because it ensures the per-frame timing used in ICA corresponds to real frame acquisition, not delayed CPU timestamps.

---

## 💡 3. LED–DIO Synchronization (Özge Çekirge’s ICA–DIO Regression)

Once frame timestamps are corrected, each camera’s LED region is analyzed to detect blink times. The LED flashes are controlled by the SpikeGadget DIO, making them a natural link between video and neural time.

Each eye video is processed via:

```python
process_video_with_metadata(...)
```

which:
1. Extracts LED pixel regions.  
2. Runs **FastICA** to separate red/blue LED components:  
   ```python
   ica = FastICA(n_components=3, random_state=0)
   demixed = ica.fit_transform(X)
   ```
3. Classifies components via K-Means and extracts LED signals over time.  
4. Produces per-eye LED activation timestamps.

Then the DIO data are read using:

```python
extract_dio_com(dio_file_path_dict, sampling_freq)
```

This returns LED pulse times in **neural clock units** (30 kHz SpikeGadget sampling).

Finally, the **CPU → DIO regression** is performed to align the corrected video timestamps to neural time:

```python
def pred_dio_ts_from_ica_ts_and_verify(ica_ts, dio_ts, ...):
    model = LinearRegression().fit(ica_ts.reshape(-1, 1), dio_ts)
    dio_pred = model.predict(ica_ts.reshape(-1, 1))
    return dio_pred, model
```

Each eye’s LED-derived video timestamps (`ica_ts`) are linearly mapped to DIO timestamps (`dio_ts`), producing per-eye neural-aligned timestamps.

✅ **Explanation:**  
This second regression translates video time into **neural time**, correcting for both clock drift and frame offset. The slope and intercept encode the cumulative drift rate and offset between the two systems.

---

## 🧮 4. Averaging Across Eyes to Create a Global Timestamp

Because each Raspberry Pi camera runs independently, 1–2 frame misalignments remain. To unify all recordings:

```python
avg_ts_per_frame = np.mean(np.vstack(results_per_eye), axis=0)
pd.DataFrame({'Corrected Time Stamp': avg_ts_per_frame}).to_csv('stitched_framewise_ts.csv')
```

This averaging produces a single **global neural timestamp series** (`stitched_framewise_ts.csv`), representing the corrected timing for every frame in the future stitched video. The number of timestamps equals the frame count of the **shortest eye video**, ensuring alignment.

---

## 🎥 5. Stitching and Tracking

- **`join_views.py`** visually merges the 12 eye videos (frame 0 aligned, truncated to the shortest) but performs **no timing correction**.  
- **`TrackerYolov3-Colab.py`** applies the global neural timestamps from `stitched_framewise_ts.csv` to the corresponding frames in `stitched.mp4`.

Thus, each frame in the stitched video inherits a **true neural-synchronized timestamp**, allowing behavioral detections to be precisely aligned with electrophysiological events.

---

## ✅ Summary

| Stage | Purpose | Function(s) | Output |
|:------|:---------|:-------------|:---------|
| GPU → CPU regression | Corrects frame capture delay | `pred_cpu_ts_from_gpu_ts()` | Corrected per-frame timestamps |
| CPU → DIO regression | Maps corrected frame times to neural time | `pred_dio_ts_from_ica_ts_and_verify()` | Per-eye neural timestamps |
| Averaging | Combines per-eye results into one | numpy.mean() | `stitched_framewise_ts.csv` |

Together, these steps ensure every frame is synchronized to the neural data with sub-frame accuracy, independent of visual stitching.

