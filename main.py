
import os
from pathlib import Path
import zipfile
import urllib.request as request
import logging
import yaml
from box import ConfigBox

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')
logger = logging.getLogger(__name__)

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE_PATH = PROJECT_ROOT / "config" / "config.yaml"
PARAMS_FILE_PATH = PROJECT_ROOT / "params.yaml"

# -----------------------------
# Utility functions
# -----------------------------
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    if not path_to_yaml.exists():
        raise FileNotFoundError(f"YAML file not found: {path_to_yaml}")
    with open(path_to_yaml) as f:
        content = yaml.safe_load(f)
    logger.info(f"Loaded YAML file: {path_to_yaml}")
    return ConfigBox(content)

def create_directories(paths: list):
    for path in paths:
        path = Path(path)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")

# -----------------------------
# DataIngestionConfig
# -----------------------------
class DataIngestionConfig:
    def __init__(self, root_dir, source_URL, local_data_file, unzip_dir):
        self.root_dir = Path(root_dir)
        self.source_URL = source_URL
        self.local_data_file = Path(local_data_file)
        self.unzip_dir = Path(unzip_dir)

# -----------------------------
# ConfigurationManager
# -----------------------------
class ConfigurationManager:
    def __init__(self, config_path=CONFIG_FILE_PATH, params_path=PARAMS_FILE_PATH):
        self.config = read_yaml(config_path)
        self.params = read_yaml(params_path)
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self):
        cfg = self.config.data_ingestion
        create_directories([cfg.root_dir])
        return DataIngestionConfig(
            root_dir=cfg.root_dir,
            source_URL=cfg.source_URL,
            local_data_file=cfg.local_data_file,
            unzip_dir=cfg.unzip_dir
        )

# -----------------------------
# DataIngestion
# -----------------------------
class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        if not self.config.local_data_file.exists():
            logger.info(f"Downloading file from {self.config.source_URL} ...")
            request.urlretrieve(
                url=self.config.source_URL,
                filename=self.config.local_data_file
            )
            logger.info(f"Downloaded file to {self.config.local_data_file}")
        else:
            logger.info(f"File already exists: {self.config.local_data_file}")

    def extract_zip_file(self):
        logger.info(f"Extracting {self.config.local_data_file} ...")
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)
        logger.info(f"Extracted zip to {self.config.unzip_dir}")

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    # Step 1: Config manager
    config_manager = ConfigurationManager()
    
    # Step 2: Data ingestion config
    data_ingestion_config = config_manager.get_data_ingestion_config()
    
    # Step 3: Data ingestion
    data_ingestion = DataIngestion(config=data_ingestion_config)
    data_ingestion.download_file()
    data_ingestion.extract_zip_file()

    logger.info("Data ingestion completed successfully!")
