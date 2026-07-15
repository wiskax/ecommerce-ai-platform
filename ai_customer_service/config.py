import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    KB_PERSIST_DIR = os.getenv("KB_PERSIST_DIR", "./ecommerce_kb")
    DATA_DIR = "./data"
    RAW_DATA_DIR = "./data/raw"
    CLEANED_DATA_DIR = "./data/cleaned"
    ANNOTATED_DATA_DIR = "./data/annotated"
    MODEL_NAME = os.getenv("MODEL_NAME", "glm-4-flash")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-2")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    TOP_K = int(os.getenv("TOP_K", "5"))

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.DATA_DIR, cls.RAW_DATA_DIR, cls.CLEANED_DATA_DIR, cls.ANNOTATED_DATA_DIR]:
            os.makedirs(d, exist_ok=True)


settings = Settings()