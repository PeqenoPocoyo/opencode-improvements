#!/usr/bin/env python3
"""analyze_sfx.py - measure a sound effect (or a folder of them) so a model that cannot listen can still judge it.

  python3 analyze_sfx.py hit.wav [more.wav | dir/] [--png outdir] [--json out.json] [--kind transient|peak|end]

Per file it prints: duration, peak / true-peak dBFS, RMS (active part) dBFS, LUFS-ish (integrated, gated; short files use the
whole file), ONSET (steepest log-envelope rise), PEAK time (sample max), ANCHOR (what sync aligns to the visual hit: for
'transient' sounds the max of the 2 ms envelope within 40 ms after the sound first reaches 25 % of its peak), attack time,
T-30 decay (peak -> -30 dB), band shares (sub 20-120, low 120-400, mid 0.4-2k, high 2-6k, air 6-16k), centroid, stereo width
(side/mid energy ratio in dB), and readable verdicts (cheap-beep detector: energy only 1-6 kHz, no sub, no tail).
--png writes a waveform + spectrogram (log-frequency) per file; LOOK at it: whoosh = a sweeping band, riser = a rising band,
impact = bright vertical click on top of a low block that decays fast.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audiolib as A  # noqa: E402


def analyze(path_or_array, sr=A.SR, kind="transient", name=None):
    if isinstance(path_or_array, str):
        x = A.read_audio(path_or_array, sr)
        name = name or os.path.basename(path_or_array)
    else:
        x = A._to_stereo(path_or_array)
        name = name or "array"
    m = A.mono(x).astype(np.float64)
    n = len(m)
    pad = np.zeros(int(0.05 * sr))
    ons = A.onsets(np.concatenate([pad, m]), sr, rise_db=6.0, floor_db=-70)
    onset = (ons[0]["t"] - 0.05) if ons else 0.0
    e = A.envelope(m, sr, 2.0)
    pk_i = int(np.argmax(np.abs(m)))
    env_pk = int(np.argmax(e))
    anchor = A.sound_anchor(m, sr, kind)
    # attack: 10 % -> 90 % of envelope peak
    ep = e.max() + 1e-12
    i10 = int(np.argmax(e > 0.1 * ep)); i90 = int(np.argmax(e > 0.9 * ep))
    attack_ms = max(0.0, (i90 - i10) / sr * 1000)
    after = e[env_pk:]
    below = np.where(after < ep * 10 ** (-30 / 20))[0]
    t30 = (below[0] / sr) if len(below) else (len(after) / sr)
    act = np.where(e > ep * 10 ** (-40 / 20))[0]
    act_dur = (act[-1] - act[0]) / sr if len(act) else 0.0
    rms = float(np.sqrt(np.mean(m[act[0]:act[-1] + 1] ** 2))) if len(act) else 0.0
    L = A.loudness(x, sr)
    bs = A.band_shares(x, sr)
    mid = (x[:, 0] + x[:, 1]) / 2; side = (x[:, 0] - x[:, 1]) / 2
    width_db = float(10 * np.log10((np.sum(side ** 2) + 1e-12) / (np.sum(mid ** 2) + 1e-12)))
    res = dict(file=name, duration_s=round(n / sr, 4), peak_db=round(A.sample_peak_db(x), 2), true_peak_db=round(A.true_peak_db(x, sr), 2),
               rms_db=round(float(A.db(rms)), 2), lufs=round(L["lufs"], 2), onset_s=round(onset, 4), peak_s=round(pk_i / sr, 4),
               anchor_s=round(anchor, 4), attack_ms=round(attack_ms, 2), t30_s=round(t30, 3), active_s=round(act_dur, 3),
               centroid_hz=round(bs["centroid_hz"]), width_db=round(width_db, 1),
               shares={k: round(100 * bs[k], 1) for k in ("sub", "low", "mid", "high", "air", "below400", "above2k")})
    v = []
    s = bs
    if s["sub"] + s["low"] < 0.08 and s["above2k"] < 0.5 and act_dur < 0.25:
        v.append("THIN: <8 % below 400 Hz and short. Fine as a TOP layer over a hit/sub; never use alone (this is the 'cheap beep' profile)")
    if t30 < 0.04 and act_dur < 0.12 and s["below400"] < 0.2:
        v.append("very short and thin: add a low thock / tail layer")
    if s["above2k"] > 0.7:
        v.append("very bright (>70 % above 2 kHz): fine for tick/glass, wrong for hits")
    if res["true_peak_db"] > -0.5:
        v.append("true peak above -0.5 dBFS: lower the level before layering")
    if attack_ms > 60 and kind == "transient":
        v.append("slow attack (>60 ms): fine for riser/whoosh/pad/bell (sync uses a designed anchor), but a HIT with this attack will feel late")
    res["verdict"] = v or ["ok"]
    return res


def spectrogram(path, png, anchor=None, sr=A.SR):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = A.mono(A.read_audio(path, sr))
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw=dict(height_ratios=[1, 2]), sharex=True)
    tt = np.arange(len(x)) / sr
    ax[0].plot(tt, x, lw=0.4)
    if anchor is not None:
        ax[0].axvline(anchor, color="r", lw=0.8)
    ax[0].set_title(os.path.basename(path))
    f, t, S = signal.spectrogram(x, sr, nperseg=1024, noverlap=896, window="hann")
    ax[1].pcolormesh(t, f, 10 * np.log10(S + 1e-12), shading="auto", vmin=-110, vmax=-30, cmap="magma")
    ax[1].set_yscale("symlog", linthresh=500); ax[1].set_ylim(20, 16000)
    if anchor is not None:
        ax[1].axvline(anchor, color="c", lw=0.8)
    ax[1].set_xlabel("s"); ax[1].set_ylabel("Hz")
    fig.tight_layout(); os.makedirs(os.path.dirname(os.path.abspath(png)), exist_ok=True); fig.savefig(png, dpi=90); plt.close(fig)


def sheet(files, png, cols=3, sr=A.SR):
    """One image with a log-frequency spectrogram per file (read it with the image viewer to check shapes)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = (len(files) + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(5.2 * cols, 2.8 * rows), squeeze=False)
    for ax in axs.ravel():
        ax.axis("off")
    for ax, f in zip(axs.ravel(), files):
        x = A.mono(A.read_audio(f, sr))
        ax.axis("on")
        fr, t, S = signal.spectrogram(x, sr, nperseg=1024, noverlap=896, window="hann")
        ax.pcolormesh(t, fr, 10 * np.log10(S + 1e-12), shading="auto", vmin=-110, vmax=-30, cmap="magma")
        ax.set_yscale("symlog", linthresh=500); ax.set_ylim(20, 16000)
        ax.set_title(os.path.basename(f), fontsize=9); ax.tick_params(labelsize=7)
    fig.tight_layout(); os.makedirs(os.path.dirname(os.path.abspath(png)), exist_ok=True); fig.savefig(png, dpi=80); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--png", metavar="DIR")
    ap.add_argument("--json", metavar="FILE")
    ap.add_argument("--sheet", metavar="PNG", help="one contact sheet of spectrograms for all inputs")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--kind", default="transient", choices=["transient", "peak", "end"])
    a = ap.parse_args()
    files = []
    for i in a.inputs:
        files += sorted(glob.glob(os.path.join(i, "*.wav"))) if os.path.isdir(i) else [i]
    rows = []
    print(f"{'file':<24}{'dur':>6}{'pk':>7}{'tp':>7}{'LUFS':>7}{'onset':>8}{'anchor':>8}{'att ms':>7}{'T30':>6}{'cent':>6} sub/low/mid/high/air %")
    for f in files:
        r = analyze(f, kind=a.kind)
        rows.append(r)
        sh = r["shares"]
        print(f"{r['file']:<24}{r['duration_s']:>6.2f}{r['peak_db']:>7.1f}{r['true_peak_db']:>7.1f}{r['lufs']:>7.1f}{r['onset_s']*1000:>7.1f}m{r['anchor_s']*1000:>7.1f}m{r['attack_ms']:>7.1f}{r['t30_s']:>6.2f}{r['centroid_hz']:>6} "
              f"{sh['sub']:.0f}/{sh['low']:.0f}/{sh['mid']:.0f}/{sh['high']:.0f}/{sh['air']:.0f}  {'; '.join(r['verdict'])}")
        if a.png:
            spectrogram(f, os.path.join(a.png, os.path.splitext(os.path.basename(f))[0] + ".png"), r["anchor_s"])
    if a.sheet:
        sheet(files, a.sheet, a.cols)
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
