#!/usr/bin/env python3
"""
Fine‑tune Whisper‑small on a pre‑prepared dataset directory.
"""

import mlflow
mlflow.set_tracking_uri("http://129.114.26.114:8000/")
mlflow.enable_system_metrics_logging()
mlflow.transformers.autolog(log_models=True)

import os, argparse, evaluate, torch
from datasets import load_from_disk
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)

# ---------- Same collator you used ----------
from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int
    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]):
        input_feats = [{"input_features": f["input_features"]} for f in features]
        batch       = self.processor.feature_extractor.pad(input_feats, return_tensors="pt")

        label_feats  = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_feats, return_tensors="pt")
        labels       = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch
# ------------------------------------------------------------

def compute_metrics_fn(tokenizer):
    wer_metric = evaluate.load("wer")
    def _compute(eval_pred):
        preds, labels = eval_pred.predictions, eval_pred.label_ids
        labels[labels == -100] = tokenizer.pad_token_id
        pred_str  = tokenizer.batch_decode(preds,   skip_special_tokens=True)
        label_str = tokenizer.batch_decode(labels, skip_special_tokens=True)
        return {"wer": 100 * wer_metric.compute(predictions=pred_str, references=label_str)}
    return _compute


def main(args):
    processor = WhisperProcessor.from_pretrained(args.model_name, language="English", task="transcribe")
    model     = WhisperForConditionalGeneration.from_pretrained(args.model_name)

    # ensure generation config
    model.generation_config.update(language="English", task="transcribe", forced_decoder_ids=None)

    dsdict = load_from_disk(args.data_dir)
    print(f"Loaded dataset: {dsdict}")

    collator = DataCollatorSpeechSeq2SeqWithPadding(
        processor=processor,
        decoder_start_token_id=model.config.decoder_start_token_id,
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        learning_rate=args.lr,
        logging_steps=25,
        logging_strategy="steps",
        fp16=True,
        gradient_checkpointing=False,
        save_steps=500,
        eval_strategy="steps",
        predict_with_generate=True,
        report_to=None,
        fp16_full_eval=True,
    )

    trainer = Seq2SeqTrainer(
        args=training_args,
        model=model,
        train_dataset=dsdict["train"],
        eval_dataset=dsdict["test"],
        data_collator=collator,
        compute_metrics=compute_metrics_fn(processor.tokenizer),
        tokenizer=processor.tokenizer,
    )

    with mlflow.start_run(run_name="whisper_small_finetune"):
        trainer.train()
        output_path = os.path.join(training_args.output_dir, "whisper-small-finetuned")
        
        trainer.save_model(output_path)
        processor.save_pretrained(output_path)

        # Log model artifacts
        mlflow.log_artifacts(output_path, artifact_path="whisper_model")

        # Log training args
        with open(os.path.join(output_path, "training_args.txt"), "w") as f:
            f.write(str(training_args))
        mlflow.log_artifact(os.path.join(output_path, "training_args.txt"), artifact_path="configs")

    print("🏁  Training complete.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",  default="./prepared_nptel")
    p.add_argument("--output_dir", default="./whisper-small-run")
    p.add_argument("--model_name", default="openai/whisper-small")
    p.add_argument("--epochs",    type=int,   default=3)
    p.add_argument("--batch",     type=int,   default=16)
    p.add_argument("--lr",        type=float, default=1e-5)
    args = p.parse_args()
    main(args)


# Run Training

# python train_whisper_small.py \
#   --data_dir  ./prepared_nptel \
#   --output_dir ./whisper-small-fast