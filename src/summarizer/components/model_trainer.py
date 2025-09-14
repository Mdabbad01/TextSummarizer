import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments
)


class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config.model_ckpt)
        self.tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_name)

    def load_dataset(self, path: str) -> Dataset:
        df = pd.read_csv(path)
        df["dialogue"] = df["dialogue"].astype(str).fillna("")
        df["summary"] = df["summary"].astype(str).fillna("")
        return Dataset.from_pandas(df)

    def tokenize_function(self, examples: dict) -> dict:
        dialogues = [str(x) for x in examples["dialogue"]]
        summaries = [str(x) for x in examples["summary"]]

        inputs = self.tokenizer(
            dialogues,
            max_length=256,
            truncation=True,
            padding="max_length"
        )

        targets = self.tokenizer(
            summaries,
            max_length=64,
            truncation=True,
            padding="max_length"
        )

        inputs["labels"] = targets["input_ids"]
        return inputs

    def train(self, train_path: str, eval_path: str):
        train_dataset = self.load_dataset(train_path).map(self.tokenize_function, batched=True)
        eval_dataset = self.load_dataset(eval_path).map(self.tokenize_function, batched=True)

        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)

        args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            save_total_limit=1,
            push_to_hub=False
        )

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )

        trainer.train()

        self.model.save_pretrained(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)
        print(f"✅ Model saved at {self.config.output_dir}")
