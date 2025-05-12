#!/usr/bin/env python3
"""
Retraining script for Whisper-small with user feedback data from MinIO.
"""

import os
import argparse

import mlflow
import torch
import boto3
import evaluate
from datasets import load_from_disk, Dataset, concatenate_datasets, Audio
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer
)
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# ---------- Same collator you used ----------
@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]):
        input_feats = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_feats, return_tensors="pt")

        label_feats = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_feats, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

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
        pred_str  = tokenizer.batch_decode(preds, skip_special_tokens=True)
        label_str = tokenizer.batch_decode(labels, skip_special_tokens=True)
        return {"wer": 100 * wer_metric.compute(predictions=pred_str, references=label_str)}
    return _compute


def download_feedback_samples(bucket_name, prefix, local_dir, endpoint_url=None):
    os.makedirs(local_dir, exist_ok=True)
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id="project48",
        aws_secret_access_key="project48",
    )
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith((".wav", ".txt")):
                dest_path = os.path.join(local_dir, os.path.basename(key))
                s3.download_file(bucket_name, key, dest_path)
    return local_dir


def prepare_feedback_dataset(feedback_dir, processor):
    entries = []
    for fname in os.listdir(feedback_dir):
        if fname.lower().endswith(".wav"):
            base = os.path.splitext(fname)[0]
            wav_path = os.path.join(feedback_dir, fname)
            txt_path = os.path.join(feedback_dir, base + ".txt")
            if os.path.exists(txt_path):
                with open(txt_path, "r") as f:
                    text = f.read().strip()
                entries.append({"audio": wav_path, "text": text})
    dataset = Dataset.from_list(entries)
    dataset = dataset.cast_column("audio", Audio(sampling_rate=processor.feature_extractor.sampling_rate))
    def preprocess(batch):
        inputs = processor.feature_extractor(batch["audio"]["array"], sampling_rate=processor.feature_extractor.sampling_rate)
        labels = processor.tokenizer(batch["text"]).input_ids
        return {"input_features": inputs.input_features[0], "labels": labels}
    processed = dataset.map(preprocess, remove_columns=dataset.column_names)
    return processed


def main(args):
    # Set MLflow tracking and autologging
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.enable_system_metrics_logging()
    mlflow.transformers.autolog(log_models=True)

    # Download new user feedback samples
    feedback_dir = download_feedback_samples(
        bucket_name=args.bucket_name,
        prefix=args.feedback_prefix,
        local_dir=os.path.join(args.output_dir, "userfeedback"),
        endpoint_url=args.minio_endpoint_url,
    )

    # Initialize processor and model
    processor = WhisperProcessor.from_pretrained(args.model_name, language="English", task="transcribe")
    model = WhisperForConditionalGeneration.from_pretrained(args.model_name)
    model.generation_config.update(language="English", task="transcribe", forced_decoder_ids=None)

    # Load existing processed dataset
    dsdict = load_from_disk(args.data_dir)

    # Prepare dataset from feedback samples
    new_ds = prepare_feedback_dataset(feedback_dir, processor)

    # Combine train datasets
    train_ds = concatenate_datasets([dsdict["train"], new_ds])
    eval_ds = dsdict["test"]

    # Data collator and training arguments
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

    # Set MLflow experiment and run
    mlflow.set_experiment("retraining-whisper-small")
    with mlflow.start_run(run_name="retraining-whisper-small"):
        trainer = Seq2SeqTrainer(
            args=training_args,
            model=model,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            data_collator=collator,
            compute_metrics=compute_metrics_fn(processor.tokenizer),
            tokenizer=processor.tokenizer,
        )
        trainer.train()

        # Save and log model
        output_path = os.path.join(args.output_dir, "whisper-small-retrained")
        trainer.save_model(output_path)
        processor.save_pretrained(output_path)
        mlflow.log_artifacts(output_path, artifact_path="whisper_model")

        # Log training arguments
        args_file = os.path.join(output_path, "training_args.txt")
        with open(args_file, "w") as f:
            f.write(str(training_args))
        mlflow.log_artifact(args_file, artifact_path="configs")

    print("🏁 Retraining complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./prepared_nptel", help="Path to existing processed dataset directory")
    parser.add_argument("--output_dir", type=str, default="./whisper-retrained", help="Output directory for retrained model")
    parser.add_argument("--model_name", type=str, default="openai/whisper-small", help="Pretrained model name")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size per device")
    parser.add_argument("--lr", type=float, default=1e-5, help="Learning rate")
    parser.add_argument("--tracking_uri", type=str, default="http://129.114.26.114:8000/", help="MLflow tracking URI")
    parser.add_argument("--bucket_name", type=str, default="mlflow-artifacts", help="MinIO bucket name for feedback artifacts")
    parser.add_argument("--feedback_prefix", type=str, default="userfeedback", help="Prefix for feedback files in the bucket")
    parser.add_argument("--minio_endpoint_url", type=str, default="http://129.114.26.114:9000/", help="MinIO endpoint URL (e.g. http://minio:9000)")
    args = parser.parse_args()
    main(args)