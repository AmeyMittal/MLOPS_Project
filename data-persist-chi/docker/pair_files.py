import os
import shutil

wav_dir = "nptelfinal/wav"
txt_dir = "nptelfinal/txt"
out_dir = "/mnt/data/paired"  

# Ensure output directory exists
os.makedirs(out_dir, exist_ok=True)

# Get base filenames (without extensions)
wavs = {f[:-4] for f in os.listdir(wav_dir) if f.endswith('.wav')}
txts = {f[:-4] for f in os.listdir(txt_dir) if f.endswith('.txt')}
common = wavs & txts


# Copy matched files
for name in common:
    shutil.copy(os.path.join(wav_dir, f"{name}.wav"), os.path.join(out_dir, f"{name}.wav"))
    shutil.copy(os.path.join(txt_dir, f"{name}.txt"), os.path.join(out_dir, f"{name}.txt"))

# Report unmatched files
missing = wavs ^ txts
if missing:
    print("Warning: Unmatched files:", missing)
else:
    print(f"✅ Paired {len(common)} files.")


