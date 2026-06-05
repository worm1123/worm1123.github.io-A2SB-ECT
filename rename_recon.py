import os
import shutil
import glob

# ─────────────────────────────────────────
# 配置路径
# ─────────────────────────────────────────
INPUT_DIR  = r"A2SB-ECT/cutoff_freq=4000"   # 包含子文件夹的根目录
OUTPUT_DIR = r"Ground_Truth"  # 复制目标文件夹

# ─────────────────────────────────────────
# 创建输出文件夹
# ─────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 遍历子文件夹
# ─────────────────────────────────────────
count_found   = 0
count_skipped = 0

for entry in sorted(os.scandir(INPUT_DIR), key=lambda e: e.name):
    if not entry.is_dir():
        continue  # 跳过非文件夹

    subfolder_name = entry.name
    subfolder_path = entry.path

    # ── 用 os.listdir 代替 glob，避免 [] 被当作通配符 ──
    try:
        all_files = os.listdir(subfolder_path)
    except PermissionError:
        print(f"  [错误] 无权限访问：{subfolder_name}")
        count_skipped += 1
        continue

    # 查找文件名包含 "recon"（不区分大小写）且以 .wav 结尾的文件
    recon_files = [
        f for f in all_files
        if f.lower().endswith(".wav") and "original" in f.lower()
    ]

    if not recon_files:
        print(f"  [跳过] {subfolder_name}（未找到 recon wav）")
        # 调试：打印该文件夹下所有 wav 文件名，方便排查
        wav_files = [f for f in all_files if f.lower().endswith(".wav")]
        if wav_files:
            print(f"         该文件夹内的 wav 文件：{wav_files}")
        else:
            print(f"         该文件夹内无任何 wav 文件")
        count_skipped += 1
        continue

    if len(recon_files) > 1:
        print(f"  [警告] {subfolder_name} 下找到多个 recon wav，仅处理第一个：{recon_files[0]}")

    src_filename = recon_files[0]
    src_path     = os.path.join(subfolder_path, src_filename)
    dst_filename = f"{subfolder_name}.wav"
    dst_path     = os.path.join(OUTPUT_DIR, dst_filename)

    shutil.copy2(src_path, dst_path)
    print(f"  [完成] {src_filename}  →  {dst_filename}")
    count_found += 1

# ─────────────────────────────────────────
# 汇总
# ─────────────────────────────────────────
print(f"\n处理完毕：共复制 {count_found} 个文件，跳过 {count_skipped} 个子文件夹。")
print(f"输出目录：{OUTPUT_DIR}")