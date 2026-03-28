"""
Configuration management for the FastAPI backend.

Loads configuration from:
1. Environment variables (highest priority)
2. .env file
3. config.yaml
4. Default values (lowest priority)
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Application configuration."""

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Fashn.ai API configuration
    FASHN_API_KEY: str = os.getenv("FASHN_API_KEY", "")
    FASHN_BASE_URL: str = "https://api.fashn.ai/v1"
    FASHN_MODEL_ID: str = "viton_hd"
    FASHN_TIMEOUT: int = int(os.getenv("FASHN_TIMEOUT", "120"))

    # Device configuration
    DEVICE: str = os.getenv("DEVICE", "cpu")

    # Data directories
    DATA_DIR: Path = Path(__file__).parent / "data"
    PERSONS_DIR: Path = DATA_DIR / "persons"
    WARDROBE_DIR: Path = DATA_DIR / "wardrobe"
    CONFIG_PATH: Path = Path(__file__).parent.parent / "configs" / "config.yaml"

    # CORS configuration
    CORS_ORIGINS: list = ["*"]  # In production, restrict to specific domains
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # File upload configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}

    # Try-on configuration
    TRYON_CATEGORY: str = "auto"  # Options: "tops", "bottoms", "one-pieces", "auto"
    TRYON_TIMEOUT: int = int(os.getenv("TRYON_TIMEOUT", "180"))

    # Segmentation configuration
    SEGMENTATION_DEVICE: str = os.getenv("SEGMENTATION_DEVICE", "cpu")
    SEGMENTATION_BOX_THRESHOLD: float = 0.3
    SEGMENTATION_TEXT_THRESHOLD: float = 0.25

    # Cache configuration
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "False").lower() == "true"
    CACHE_TTL: int = 3600  # 1 hour

    @classmethod
    def from_yaml(cls, config_path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    @classmethod
    def load(cls) -> None:
        """Load configuration from all sources."""
        # Load YAML config if available
        yaml_config = cls.from_yaml(cls.CONFIG_PATH)

        # Update from YAML (lower priority)
        if "fashn" in yaml_config:
            cls.FASHN_API_KEY = yaml_config["fashn"].get("api_key", cls.FASHN_API_KEY)
            cls.FASHN_BASE_URL = yaml_config["fashn"].get("base_url", cls.FASHN_BASE_URL)
            cls.FASHN_MODEL_ID = yaml_config["fashn"].get("model_id", cls.FASHN_MODEL_ID)
            cls.FASHN_TIMEOUT = yaml_config["fashn"].get("timeout", cls.FASHN_TIMEOUT)

        if "segmentation" in yaml_config:
            cls.SEGMENTATION_DEVICE = yaml_config["segmentation"].get(
                "device", cls.SEGMENTATION_DEVICE
            )
            cls.SEGMENTATION_BOX_THRESHOLD = yaml_config["segmentation"].get(
                "box_threshold", cls.SEGMENTATION_BOX_THRESHOLD
            )
            cls.SEGMENTATION_TEXT_THRESHOLD = yaml_config["segmentation"].get(
                "text_threshold", cls.SEGMENTATION_TEXT_THRESHOLD
            )

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []

        if not cls.FASHN_API_KEY:
            errors.append("FASHN_API_KEY is not set")

        if not cls.PERSONS_DIR.exists():
            cls.PERSONS_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.WARDROBE_DIR.exists():
            cls.WARDROBE_DIR.mkdir(parents=True, exist_ok=True)

        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append(f"Invalid port: {cls.PORT}")

        if cls.MAX_FILE_SIZE < 1024:  # At least 1 KB
            errors.append(f"Invalid MAX_FILE_SIZE: {cls.MAX_FILE_SIZE}")

        return len(errors) == 0, errors

    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary."""
        return {
            "server": {
                "host": cls.HOST,
                "port": cls.PORT,
                "debug": cls.DEBUG,
                "log_level": cls.LOG_LEVEL,
            },
            "fashn": {
                "api_key": cls.FASHN_API_KEY[:10] + "..." if cls.FASHN_API_KEY else "NOT_SET",
                "base_url": cls.FASHN_BASE_URL,
                "model_id": cls.FASHN_MODEL_ID,
                "timeout": cls.FASHN_TIMEOUT,
            },
            "segmentation": {
                "device": cls.SEGMENTATION_DEVICE,
            },
            "paths": {
                "data_dir": str(cls.DATA_DIR),
                "persons_dir": str(cls.PERSONS_DIR),
                "wardrobe_dir": str(cls.WARDROBE_DIR),
                "config_path": str(cls.CONFIG_PATH),
            },
            "limits": {
                "max_file_size": cls.MAX_FILE_SIZE,
                "tryon_timeout": cls.TRYON_TIMEOUT,
            },
        }


# Load configuration on import
Config.load()
