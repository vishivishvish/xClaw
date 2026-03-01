# Structured Logging in Python

Summary:
Uses logging module for structured logs.
Encourages log levels and formatting.
Improves debugging visibility.

---

import logging

logging.basicConfig(level=logging.INFO)

def log_message(msg):
    logging.info(msg)