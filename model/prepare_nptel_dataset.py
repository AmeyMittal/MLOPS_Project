#!/usr/bin/env python3
"""
Prepare the NPTEL paired speech‑text data for Whisper fine‑tuning.
"""

import os, argparse, multiprocessing, random
from tqdm import tqdm
from datasets import Dataset, DatasetDict, Audio
from transformers import WhisperProcessor, WhisperTokenizer

def make_samples(data_dir: str):
    samples = []
    for fname in tqdm(os.listdir(data_dir), desc="Scanning .wav files"):
        if fname.endswith(".wav"):
            base = fname[:-4]
            wav = os.path.join(data_dir, f"{base}.wav")
            txt = os.path.join(data_dir, f"{base}.txt")
            if os.path.exists(txt):
                with open(txt) as f:
                    transcript = f.read().strip()
                samples.append({"audio": wav, "text": transcript})
    print(f"Collected {len(samples):,} (wav, txt) pairs")
    return samples


def preprocess(example, processor, tokenizer):
    audio = example["audio"]
    example["input_features"] = processor.feature_extractor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_features[0]
    example["labels"] = tokenizer(example["text"]).input_ids
    return example


def main(args):
    # ---------- 1. Init tokenizer / processor ----------
    tokenizer  = WhisperTokenizer.from_pretrained(args.model_name, language="English", task="transcribe")
    processor  = WhisperProcessor.from_pretrained(args.model_name, language="English", task="transcribe")

    # ---------- 2. Build dataset ----------
    samples = make_samples(args.data_dir)
    ds      = Dataset.from_list(samples).cast_column("audio", Audio(sampling_rate=16_000))
    ds      = ds.train_test_split(test_size=args.test_size, seed=args.seed)

    # ---------- 3. Feature extraction & label encoding ----------
    num_proc = args.num_proc or multiprocessing.cpu_count()
    ds = ds.map(
        preprocess,
        fn_kwargs={"processor": processor, "tokenizer": tokenizer},
        remove_columns=["audio", "text"],
        num_proc=num_proc,
        desc="Extracting log‑Mel + tokenising",
    )

    # ---------- 4. Save ----------
    ds.save_to_disk(args.out_dir)
    print(f"Saved pre‑processed dataset to →  {args.out_dir}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",  default="/mnt/nptel/paired")
    p.add_argument("--out_dir",   default="./prepared_nptel")
    p.add_argument("--model_name", default="openai/whisper-small")
    p.add_argument("--test_size", type=float, default=0.10)
    p.add_argument("--seed",      type=int,   default=42)
    p.add_argument("--num_proc",  type=int,   default=None)
    args = p.parse_args()
    main(args)

# Run using ->

# python prepare_nptel_dataset.py \
#   --data_dir /mnt/nptel/paired \
#   --out_dir  ./prepared_nptel