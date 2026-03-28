"""
Health check and monitoring utilities for the backend.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitor server health and component status."""

    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0

    def get_status(self) -> Dict[str, Any]:
        """Get current server status."""
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "uptime_readable": self._format_uptime(uptime_seconds),
            "stats": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": (
                    self.error_count / self.request_count
                    if self.request_count > 0
                    else 0
                ),
            },
            "environment": self._get_environment_info(),
        }

    def check_dependencies(self) -> Dict[str, str]:
        """Check if required dependencies are available."""
        deps = {}

        # Check if FastAPI is available
        try:
            import fastapi
            deps["fastapi"] = "available"
        except ImportError:
            deps["fastapi"] = "missing"

        # Check if Pillow is available
        try:
            from PIL import Image
            deps["pillow"] = "available"
        except ImportError:
            deps["pillow"] = "missing"

        # Check if PyYAML is available
        try:
            import yaml
            deps["pyyaml"] = "available"
        except ImportError:
            deps["pyyaml"] = "missing"

        # Check if requests is available
        try:
            import requests
            deps["requests"] = "available"
        except ImportError:
            deps["requests"] = "missing"

        # Check optional dependencies for segmentation
        try:
            import torch
            deps["torch"] = "available"
        except ImportError:
            deps["torch"] = "missing (optional)"

        try:
            from rembg import remove
            deps["rembg"] = "available"
        except ImportError:
            deps["rembg"] = "missing (optional)"

        # Check CUDA availability if torch is available
        if deps.get("torch") == "available":
            try:
                import torch
                if torch.cuda.is_available():
                    deps["cuda"] = f"available ({torch.cuda.get_device_name(0)})"
                else:
                    deps["cuda"] = "not available"
            except Exception as e:
                deps["cuda"] = f"error: {str(e)}"

        return deps

    def check_data_directories(self) -> Dict[str, bool]:
        """Check if required data directories exist."""
        from config import Config

        dirs = {
            "persons": Config.PERSONS_DIR.exists(),
            "wardrobe": Config.WARDROBE_DIR.exists(),
            "data": Config.DATA_DIR.exists(),
        }

        return dirs

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        try:
            import platform
            return {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor() or "unknown",
            }
        except Exception as e:
            logger.warning(f"Could not get environment info: {e}")
            return {}

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)


# Global monitor instance
monitor = HealthMonitor()


def increment_request():
    """Increment request counter."""
    monitor.request_count += 1


def increment_error():
    """Increment error counter."""
    monitor.error_count += 1


def get_health_report() -> Dict[str, Any]:
    """Get comprehensive health report."""
    return {
        "status": monitor.get_status(),
        "dependencies": monitor.check_dependencies(),
        "directories": monitor.check_data_directories(),
    }
