from dataclasses import dataclass
from src.summarizer.entity.dataingestionconfig import (
    DataIngestionConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)
from src.summarizer.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from src.summarizer.utils.common import read_yaml, create_directories


class ConfigurationManager:
    def __init__(self, config_filepath=CONFIG_FILE_PATH, params_filepath=PARAMS_FILE_PATH):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        # Create artifacts root directory
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion
        return DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        return DataTransformationConfig(
            root_dir=config.root_dir,
            train_path=config.train_path,
            test_path=config.test_path,
            val_path=config.val_path
        )

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.training
        return ModelTrainerConfig(
            root_dir=config.output_dir,
            model_ckpt=config.model_name,
            tokenizer_name=config.tokenizer_name,
            output_dir=config.output_dir,
            num_train_epochs=config.num_train_epochs,
            per_device_train_batch_size=config.per_device_train_batch_size,
            per_device_eval_batch_size=config.per_device_eval_batch_size,
            learning_rate=config.get("learning_rate", 5e-5),
            weight_decay=config.get("weight_decay", 0.0),
            logging_steps=config.get("logging_steps", 10),
            evaluation_strategy=config.get("evaluation_strategy", "epoch"),
            eval_steps=config.get("eval_steps", 100),
            save_steps=config.get("save_steps", 500),
            gradient_accumulation_steps=config.get("gradient_accumulation_steps", 1)
        )
