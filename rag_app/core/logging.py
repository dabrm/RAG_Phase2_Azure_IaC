import logging

# Root = WARNING, so third-party libraries stay quiet by default
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Only your app logs at INFO
logger = logging.getLogger("rag-app")
logger.setLevel(logging.INFO)

# Belt and braces for the chattiest libraries
for noisy in ("azure", "httpx", "httpx2", "httpcore", "httpcore2", "openai"):
    logging.getLogger(noisy).setLevel(logging.WARNING)