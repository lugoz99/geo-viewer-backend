# app/utils/logging.py

import logging  # Python’s built-in logging module
import sys  # for directing logs to the console
import os  # for reading environment variables and handling files

# -----------------------------
# 1️⃣ Read environment
# -----------------------------
# Get the ENVIRONMENT variable from your .env file
# Default to "development" if not set
ENV = os.getenv("ENVIRONMENT", "development")

# -----------------------------
# 2️⃣ Create the logger
# -----------------------------
# Create a logger with a unique name "app_logger"
logger = logging.getLogger("app_logger")

# Set the log level depending on the environment
# Development: INFO → logs all important messages
# Production: ERROR → logs only critical errors
logger.setLevel(logging.INFO if ENV == "development" else logging.ERROR)

# -----------------------------
# 3️⃣ Define log format
# -----------------------------
# Define how each log message should look
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
# - %(asctime)s → timestamp
# - %(levelname)s → log level (INFO, ERROR, WARNING, etc.)
# - %(name)s → logger name (app_logger)
# - %(message)s → the log message you send

# -----------------------------
# 4️⃣ Console handler
# -----------------------------
# Logs are sent to the console (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)  # apply the defined format
logger.addHandler(console_handler)  # attach the handler to the logger

# -----------------------------
# 5️⃣ File handler (production only)
# -----------------------------
# In production, save errors to a file
if ENV != "development":
    # Create "logs" directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Handler that writes logs to "logs/error.log"
    file_handler = logging.FileHandler("logs/error.log")
    file_handler.setFormatter(formatter)  # apply format
    logger.addHandler(file_handler)  # attach to logger

# -----------------------------
# 6️⃣ Using the logger
# -----------------------------
# Now you can use:
# - logger.info("App started")
# - logger.warning("Something might be wrong")
# - logger.error("An error occurred")
# - logger.critical("Critical issue!")
# - logger.exception("Exception with full stack trace")
