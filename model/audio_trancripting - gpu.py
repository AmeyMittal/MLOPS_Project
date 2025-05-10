import transformers
print(transformers.__version__)


import torch

if torch.cuda.is_available():
    print("Using GPU:", torch.cuda.get_device_name(0))
else:
    print("No GPU available.")


import random
from datasets import load_dataset, Audio, DatasetDict
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
    pipeline,
)

import os
from datasets import Dataset
from tqdm import tqdm

data_dir = "/mnt/nptel/paired"
samples = []

# Wrap with tqdm for progress
for fname in tqdm(os.listdir(data_dir), desc="Loading data"):
    if fname.endswith(".wav"):
        base = fname.replace(".wav", "")
        audio_path = os.path.join(data_dir, f"{base}.wav")
        text_path = os.path.join(data_dir, f"{base}.txt")

        if os.path.exists(text_path):
            with open(text_path, "r") as f:
                transcript = f.read().strip()
            samples.append({"audio": audio_path, "text": transcript})

print(f"Total samples loaded: {len(samples)}")
ds = Dataset.from_list(samples)

ds = ds.train_test_split(test_size=0.1, seed=42)


# ensure audio is resampled to 16 kHz
ds = ds.cast_column("audio", Audio(sampling_rate=16000))

from transformers import WhisperTokenizer
tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-small", language="English", task="transcribe")


from transformers import WhisperProcessor
processor = WhisperProcessor.from_pretrained("openai/whisper-small", language="English", task="transcribe")


# print(ds['train'][0])
# print(ds['test'][0])



def prepare_dataset(batch):
    # load and resample audio data from 48 to 16kHz
    audio = batch["audio"]

    # compute log-Mel input features from input audio array
    batch["input_features"] = processor.feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]

    # encode target text to label ids
    batch["labels"] = tokenizer(batch["text"]).input_ids
    return batch


ds = ds.map(prepare_dataset, remove_columns=ds.column_names["train"], num_proc=2)



from transformers import WhisperForConditionalGeneration
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

model.generation_config.language = "English"
model.generation_config.task = "transcribe"

model.generation_config.forced_decoder_ids = None

import torch

from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need different padding methods
        # first treat the audio inputs by simply returning torch tensors
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # get the tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        # pad the labels to max length
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        # if bos token is appended in previous tokenization step,
        # cut bos token here as it's append later anyways
        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels

        return batch


data_collator = DataCollatorSpeechSeq2SeqWithPadding(
    processor=processor,
    decoder_start_token_id=model.config.decoder_start_token_id,
)



import evaluate

metric = evaluate.load("wer")

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    wer = 100 * metric.compute(predictions=pred_str, references=label_str)
    print(f"WER: {wer:.2f}%")
    return {"wer": wer}

import os
os.environ["WANDB_DISABLED"] = "true"


from transformers import Seq2SeqTrainingArguments

# training_args = Seq2SeqTrainingArguments(
#     output_dir="./whisper-small-hi",
#     num_train_epochs=1,
#     per_device_train_batch_size=16,
#     gradient_accumulation_steps=1,
#     learning_rate=1e-5,
#     warmup_steps=500,
#     max_steps=4000,
#     # gradient_checkpointing=True,
#     fp16=True,
#     fp16_full_eval=True, #can use on A100 GPUs for faster evaluation
#     eval_strategy="steps",
#     per_device_eval_batch_size=8,
#     predict_with_generate=False,
#     save_steps=2000,
#     eval_steps=2000,
#     logging_steps=25,
#     logging_strategy="steps",
#     report_to=None,
#     load_best_model_at_end=True,
#     metric_for_best_model="wer",
#     greater_is_better=False,
# )

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-fast",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=1e-5,
    logging_steps=25,
    logging_strategy="steps",
    save_steps=500,
    eval_strategy="steps",
    report_to=None,
    fp16=True,
    gradient_checkpointing=False,
    predict_with_generate=True,
    fp16_full_eval=True, #can use on A100 GPUs for faster evaluation
)

from transformers import Seq2SeqTrainer

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=ds["train"],
    eval_dataset=ds["test"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.tokenizer
)

# this is just an explicit callback in case report to "none" is still not printing anything to my console.

# from transformers import TrainerCallback

# class LossPrinterCallback(TrainerCallback):
#     def on_log(self, args, state, control, logs=None, **kwargs):
#         if logs is not None:
#             print(f"Step {state.global_step} - {logs}")

# trainer.add_callback(LossPrinterCallback())


processor.save_pretrained(training_args.output_dir)

trainer.train()

trainer.save_model("whisper-small-hi-finetuned")
processor.save_pretrained("whisper-small-hi-finetuned")

import torchaudio

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# def transcribe(audio_path):
#     speech, sr = torchaudio.load(audio_path)
#     if sr != 16000:
#         resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
#         speech = resampler(speech)

#     inputs = processor(speech.squeeze(), sampling_rate=16000, return_tensors="pt")
#     inputs = {k: v.to(device) for k, v in inputs.items()}  # move to GPU if available

#     with torch.no_grad():
#         predicted_ids = model.generate(inputs["input_features"])
#         transcription = processor.tokenizer.batch_decode(predicted_ids, skip_special_tokens=True)[0]

#     return transcription

# # Run
# print(transcribe("000ace94c86177e4733f35dee57be61fda36484ad5481ab95f3694e2.wav"))
