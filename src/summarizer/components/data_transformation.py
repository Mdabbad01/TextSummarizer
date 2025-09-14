import pandas as pd
from sklearn.model_selection import train_test_split
from src.summarizer.logging import logger

class DataTransformation:
    def __init__(self, config):
        self.config = config

    def split_data(self):
        logger.info(f"Reading training data from: {self.config.train_path}")
        train_df = pd.read_csv(self.config.train_path)

        logger.info(f"Reading test data from: {self.config.test_path}")
        test_df = pd.read_csv(self.config.test_path)

        logger.info(f"Reading validation data from: {self.config.val_path}")
        val_df = pd.read_csv(self.config.val_path)

        logger.info(f"Train shape: {train_df.shape}, Test shape: {test_df.shape}, Val shape: {val_df.shape}")

        # Save to artifacts/data_transformation
        train_df.to_csv(self.config.root_dir + "/train.csv", index=False)
        test_df.to_csv(self.config.root_dir + "/test.csv", index=False)
        val_df.to_csv(self.config.root_dir + "/val.csv", index=False)

        logger.info("Data Transformation completed. Train, Test, Val saved.")
