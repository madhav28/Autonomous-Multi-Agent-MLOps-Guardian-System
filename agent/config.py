from pathlib import Path
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    model_path: str = Field("gpt-3.5-turbo", env="MODEL_PATH")
    data_dir: Path = Field(Path("./data/logs"), env="DATA_DIR")
    drift_threshold: float = Field(0.07, env="DRIFT_THRESHOLD")
    retrain_command: str = Field(
        "python pipelines/training_pipeline.py", env="RETRAIN_COMMAND"
    )

    class Config:
        env_file = ".env"

settings = Settings()

