from pathlib import Path

# Set project root to the root of your Summarizer folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

CONFIG_FILE_PATH = PROJECT_ROOT / "config" / "config.yaml"
PARAMS_FILE_PATH = PROJECT_ROOT / "params.yaml"

__all__ = ["CONFIG_FILE_PATH", "PARAMS_FILE_PATH"]
