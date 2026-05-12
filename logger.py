"""
logger.py
Rotating file logger + coloured console output.
All modules call: from logger import get_logger
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler

import colorlog
from pkg_resources import safe_name

import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # ── Console handler (coloured) ────────────────────────────────────────────
    console = colorlog.StreamHandler()
    console.setLevel(level)
    console.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
        }
    ))

    # ── Rotating file handler (daily, keep 30 days) ───────────────────────────
    os.makedirs(config.LOG_DIR, exist_ok=True)
    safe_name = (name or "app").replace(".", "_")
    log_file = os.path.join(config.LOG_DIR, f"{safe_name}.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
