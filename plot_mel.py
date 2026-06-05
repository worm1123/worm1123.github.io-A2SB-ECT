import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import glob

# ─────────────────────────────────────────
# 配置路径
# ─────────────────────────────────────────
INPUT_DIR  = r"Ground_Truth"       # 输入 WAV 文件所在文件夹
OUTPUT_DIR = r"Ground_Truth_Mel"  # 输出频谱图保存文件夹

# ─────────────────────────────────────────
# STFT / Mel 参数
# ─────────────────────────────────────────
N_FFT      = 2048
HOP_LENGTH = 128
WIN_LENGTH = 1024
N_MELS     = 256
F_MIN      = 0

# Y 轴刻度（Hz，Mel 尺度关键节点）
MEL_YTICKS = [0, 566, 1147, 2059, 3695, 6630, 11896]

# ─────────────────────────────────────────
# 全局字体 / 风格
# ─────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.linewidth":   1.0,
    "axes.labelsize":   12,
    "axes.titlesize":   12,
    "xtick.labelsize":  10,
    "ytick.labelsize":  9,
    "xtick.direction":  "out",
    "ytick.direction":  "out",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
})

# ─────────────────────────────────────────
# 创建输出文件夹
# ─────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 获取所有 WAV 文件
# ─────────────────────────────────────────
wav_files = glob.glob(os.path.join(INPUT_DIR, "*.wav"))

if not wav_files:
    print(f"未找到任何 WAV 文件：{INPUT_DIR}")
else:
    print(f"共找到 {len(wav_files)} 个 WAV 文件，开始处理...")

# ─────────────────────────────────────────
# 逐文件绘制并保存
# ─────────────────────────────────────────
for audio_path in wav_files:
    basename   = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = os.path.join(OUTPUT_DIR, f"{basename}.png")

    try:
        y, sr = librosa.load(audio_path, sr=None)
    except Exception as e:
        print(f"  [跳过] 无法加载 {audio_path}：{e}")
        continue

    fmax_actual = sr // 2

    # ── 计算 Mel 频谱图 ───────────────────
    mel_spec = librosa.feature.melspectrogram(
        y=y, sr=sr,
        n_fft=N_FFT, hop_length=HOP_LENGTH, win_length=WIN_LENGTH,
        window="hann", n_mels=N_MELS,
        fmin=F_MIN, fmax=fmax_actual,
        power=2.0,
    )
    mel_db = librosa.power_to_db(mel_spec, ref=np.max, top_db=80)

    # ── 创建单图 ──────────────────────────
    fig, ax = plt.subplots(figsize=(7, 4))

    librosa.display.specshow(
        mel_db,
        sr=sr, hop_length=HOP_LENGTH,
        fmin=F_MIN, fmax=fmax_actual,
        x_axis="time", y_axis="mel",
        cmap="viridis", vmin=-80, vmax=0,
        ax=ax,
    )

    # ── 坐标轴标签 ────────────────────────
    ax.set_xlabel("Time (seconds)", labelpad=4)
    ax.set_ylabel("Frequency (Mel)", labelpad=4)

    # ── Y 轴刻度 ──────────────────────────
    yticks = [f for f in MEL_YTICKS if f <= fmax_actual]
    yticks.append(fmax_actual)
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(int(f)) for f in yticks])
    ax.yaxis.set_minor_locator(ticker.NullLocator())

    # ── X 轴 minor ticks ──────────────────
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    # ── 四边框保留 ────────────────────────
    for spine in ax.spines.values():
        spine.set_visible(True)

    # ── 保存 ──────────────────────────────
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [完成] {output_path}")

print("全部处理完毕。")