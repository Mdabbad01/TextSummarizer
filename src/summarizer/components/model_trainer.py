import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments
)
import torch
import os


class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # If trained model already exists, load it
        if os.path.exists(config.output_dir) and os.listdir(config.output_dir):
            print(f"✅ Found existing model at {config.output_dir}, loading instead of retraining...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(config.output_dir).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(config.output_dir)
        else:
            # Load fresh model + tokenizer
            self.model = AutoModelForSeq2SeqLM.from_pretrained(config.model_ckpt).to(self.device)
            if self.device == "cuda":
                self.model.gradient_checkpointing_enable()
            self.tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_name)

    def load_dataset(self, path: str) -> Dataset:
        df = pd.read_csv(path)
        df["dialogue"] = df["dialogue"].astype(str).fillna("")
        df["summary"] = df["summary"].astype(str).fillna("")
        return Dataset.from_pandas(df)

    def tokenize_function(self, examples: dict) -> dict:
        inputs = self.tokenizer(
            examples["dialogue"],
            max_length=128,
            truncation=True,
            padding="max_length"
        )
        targets = self.tokenizer(
            examples["summary"],
            max_length=32,
            truncation=True,
            padding="max_length"
        )
        inputs["labels"] = targets["input_ids"]
        return inputs

    def train(self, train_path: str, eval_path: str):
        # If model already trained, skip training
        if os.path.exists(self.config.output_dir) and os.listdir(self.config.output_dir):
            print(f"⚡ Skipping training since model already exists at {self.config.output_dir}")
            return

        if self.device == "cuda":
            torch.cuda.empty_cache()

        # Load and tokenize datasets
        train_dataset = self.load_dataset(train_path).map(
            self.tokenize_function,
            batched=True,
            remove_columns=["dialogue", "summary"]
        )
        eval_dataset = self.load_dataset(eval_path).map(
            self.tokenize_function,
            batched=True,
            remove_columns=["dialogue", "summary"]
        )

        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)

        args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=min(self.config.per_device_train_batch_size, 1),
            per_device_eval_batch_size=min(self.config.per_device_eval_batch_size, 1),
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            save_total_limit=1,
            fp16=False,  # keeping FP16 off for stability
            push_to_hub=False,
            no_cuda=False,
        )

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )

        # Start training
        trainer.train()

        # Save trained model
        self.model.save_pretrained(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)
        print(f"✅ Model trained and saved at {self.config.output_dir}")
