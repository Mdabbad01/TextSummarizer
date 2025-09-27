# src/summarizer/components/model_prediction.py
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class ModelPrediction:
    def __init__(self, model_path="artifacts/model"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def summarize(self, text, max_length=128, min_length=30):
        inputs = self.tokenizer([text], max_length=1024, truncation=True, return_tensors="pt").to(self.device)
        summary_ids = self.model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            early_stopping=True
        )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
