# timing.py
import time
from contextlib import contextmanager
from logger import logger


@contextmanager
def timed_step(name: str, trace_id: str):
    start = time.perf_counter()
    yield
    dur = (time.perf_counter() - start) * 1000
    logger.info(f"[{trace_id}] step={name} duration_ms={dur:.1f}")
