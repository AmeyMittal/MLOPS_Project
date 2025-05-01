import os

wavs = {f[:-4] for f in os.listdir('.') if f.endswith('.wav')}
txts = {f[:-4] for f in os.listdir('.') if f.endswith('.txt')}
common = wavs & txts

os.makedirs('paired', exist_ok=True)

for name in common:
    os.rename(f"{name}.wav", os.path.join("paired", f"{name}.wav"))
    os.rename(f"{name}.txt", os.path.join("paired", f"{name}.txt"))

missing = wavs ^ txts
if missing:
    print("Warning: Unmatched files:", missing)