from src.summarizer.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from src.summarizer.utils.common import read_yaml, create_directories
from src.summarizer.entity.dataingestionconfig import DataIngestionConfig
from pathlib import Path

class ConfigurationManager:
    def __init__(self, config_path=CONFIG_FILE_PATH, params_filepath=PARAMS_FILE_PATH):
        self.config = read_yaml(config_path)
        self.params = read_yaml(params_filepath)
        # create artifacts_root
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        cfg = self.config.data_ingestion
        create_directories([cfg.root_dir])
        return DataIngestionConfig(
            root_dir=Path(cfg.root_dir),
            source_URL=cfg.source_URL,
            local_data_file=Path(cfg.local_data_file),
            unzip_dir=Path(cfg.unzip_dir)
        )
