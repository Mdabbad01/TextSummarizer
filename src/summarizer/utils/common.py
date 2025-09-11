import os
from box.exceptions import BoxValueError
import yaml
from box import ConfigBox
from ensure import ensure_annotations
from pathlib import Path
from src.summarizer.logging import logger

@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    if not path_to_yaml.exists():
        raise FileNotFoundError(f"YAML file not found: {path_to_yaml}")
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file:{path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e

@ensure_annotations
def create_directories(paths: list, verbose=True):
    for path in paths:
        path = Path(path)  # ensure Path object
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"Created directory at: {path}")
