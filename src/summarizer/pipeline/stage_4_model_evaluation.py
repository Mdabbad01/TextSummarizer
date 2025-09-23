import torch
import pandas as pd
from datasets import Dataset
import evaluate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from src.summarizer.config.configuration import ConfigurationManager

class ModelEvaluationTrainingPipeline:
    def __init__(self):
        # -------------------- Load config --------------------
        config_manager = ConfigurationManager()  # create instance
        config = config_manager.get_model_trainer_config()  # correct method

        # -------------------- Load trained model & tokenizer --------------------
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config.output_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(config.output_dir)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def initiate_model_evaluation(self, eval_path: str):
        # -------------------- Load evaluation dataset --------------------
        df = pd.read_csv(eval_path)
        df["dialogue"] = df["dialogue"].astype(str).fillna("")
        df["summary"] = df["summary"].astype(str).fillna("")
        dataset = Dataset.from_pandas(df)

        # -------------------- Function to generate summary --------------------
        def generate_summary(text):
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=128
            ).to(self.device)
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                max_length=32,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # -------------------- Generate predictions --------------------
        predictions = [generate_summary(x) for x in dataset["dialogue"]]
        references = dataset["summary"]

        # -------------------- Compute ROUGE --------------------
        rouge = evaluate.load("rouge")
        results = rouge.compute(predictions=predictions, references=references)

        print("\n=== ROUGE Evaluation Results ===")
        for key, value in results.items():
            print(f"{key}: {value:.4f}")  # directly print float, no .mid.fmeasure

        return results
