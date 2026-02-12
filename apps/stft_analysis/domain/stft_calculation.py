from pathlib import Path
from base_core.quantities.models import Frequency, Time
import numpy as np
from scipy.signal import stft, detrend

from apps.stft_analysis.domain.config import StftAnalysisConfig
from apps.stft_analysis.domain.models import AggregateSpectrogram, ResampledScan, SpectrogramResult

BACKUP_WINDFRACT = 2

def calculate_spectrogram(resampled_scan: ResampledScan, config: StftAnalysisConfig) -> SpectrogramResult:
    
    c2t = resampled_scan.detrend()
    
    
    samplesperseg = min(
        int(len(c2t) / BACKUP_WINDFRACT),
        int(round(config.stft_window_size / config.resample_time)),
    )
    samplesperseg = max(1, samplesperseg)

    # Erzwinge ungerade Fensterlänge -> len(t_s) == len(c2t) bei hop=1
    if samplesperseg % 2 == 0:
        samplesperseg -= 1
        samplesperseg = max(1, samplesperseg)

    numoverlap = samplesperseg - 1 if samplesperseg > 1 else 0
    fs=1/config.resample_time    
    

    f, t_s, Zxx = stft(
        c2t, fs=fs,
        nperseg=samplesperseg,
        noverlap=numoverlap,
        window="blackman",
    )
    # -----
    SpecSig = (np.abs(Zxx))**2
    t_s = t_s + resampled_scan.delays[0] #convert back to ps and get time zero back
    
    delay: list[Time] = [Time(val) for val in t_s]                
    frequency: list[Frequency] = [Frequency(val) for val in f]
    
    return SpectrogramResult(
        delay=delay,
        frequency=frequency,
        power=SpecSig,
        file_path=resampled_scan.file_path,
    )

def calculate_averaged_spectrogram(
    resampled_scans: list[ResampledScan],
    config: StftAnalysisConfig
) -> AggregateSpectrogram:
    """
    Calculate the averaged spectrogram over multiple resampled scans.

    For each scan we:
      1) compute an individual spectrogram (same STFT params -> same freq axis)
      2) embed it into a 3D cube of shape (n_scans, n_freq, n_time_global)
         where n_time_global is the union of all STFT time bins.
         Time points where a scan has no data are filled with NaN.
      3) average over the scan axis using np.nanmean, so only existing
         spectrograms contribute at a given time bin.
    """
    if not resampled_scans:
        raise ValueError("resampled_scans must not be empty")

    # --- 1) Compute individual spectrograms ----------------------------
    specs: list[SpectrogramResult] = [
        calculate_spectrogram(scan, config)
        for scan in resampled_scans
    ]

    # --- 2) Check that all spectrograms share the same frequency axis --
    base_freq = np.asarray(specs[0].frequency, dtype=float)  # (n_freq,)
    n_freq = base_freq.size

    for s in specs[1:]:
        f_i = np.asarray(s.frequency, dtype=float)
        if f_i.shape != base_freq.shape or not np.allclose(f_i, base_freq):
            raise ValueError(
                "Frequency axes of individual spectrograms differ; "
                "cannot average without interpolation."
            )

    # --- 3) Build global time grid: union of all STFT time axes -------
    time_axes = [np.asarray(s.delay, dtype=float) for s in specs]  # each (n_time_i,)
    global_time = np.array(config.axis)            # (n_time_global,)
    n_time_global = global_time.size

    # --- 4) Allocate 3D cube and embed each spectrogram ---------------
    # Shape: (n_scans, n_freq, n_time_global)
    # n_freq = len(specs[0].frequency)
    # n_time_global = len(global_time)

    # cube[scan_index, freq_index, time_index]
    cube = np.full((len(specs), n_freq, n_time_global), np.nan, dtype=float)

    for i, s in enumerate(specs):
        P = np.asarray(s.power, dtype=float)          # (n_freq, n_time_i)  <- like SpecSig

        # Now shapes match: cube[i, :, idx] and P are both (n_freq, n_time_i)
        cube[i, :, :] = P

    # Average over scans -> (n_freq, n_time_global)
    avg_power = np.nanmean(cube, axis=0)
    max_val = float(np.nanmax(avg_power))
    if max_val > 0:
        avg_power = avg_power / max_val

    # --- 6) Build AggregateSpectrogram with list[list[float]] ---------
    delay_times: list[Time] = [Time(t) for t in global_time]
    freq_objs: list[Frequency] = [Frequency(f) for f in base_freq]
    file_paths: list[Path] = [scan.file_path for scan in resampled_scans]

    return AggregateSpectrogram(
        delay=delay_times,
        frequency=freq_objs,
        power=avg_power.tolist(),   # <- convert ndarray -> list[list[float]]
        file_paths=file_paths,
    )
