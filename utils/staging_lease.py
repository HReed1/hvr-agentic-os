import os
import fcntl
import time
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING_DIR = os.path.join(BASE_DIR, ".staging")
LOCK_FILE = os.path.join(STAGING_DIR, ".lock_mutex")

@contextmanager
def acquire_staging_lease(exclusive=False):
    """
    Acquires an OS-Kernel level fcntl lock over the staging directory.
    - exclusive=False (LOCK_SH): Used by Executor/QA for concurrent non-destructive reads/tests.
    - exclusive=True (LOCK_EX): Used by Architect/Auditor for promotions/teardowns.
    
    Implements a 60-second Native Backoff Mutex using fcntl.LOCK_NB to prevent hallucination recursion.
    """
    # Ensure staging directory exists so we can map a physical lockfile
    os.makedirs(STAGING_DIR, exist_ok=True)
    
    file_descriptor = open(LOCK_FILE, 'w')
    lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    
    timeout_seconds = 60
    start_time = time.time()
    
    while True:
        try:
            # LOCK_NB forcefully throws BlockingIOError instead of hanging forever
            fcntl.flock(file_descriptor.fileno(), lock_type | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.time() - start_time > timeout_seconds:
                file_descriptor.close()
                raise BlockingIOError("[ERROR] Staging Area is currently locked by another Agent context. Wait and retry.")
            
            # The Agentic Rate-Limiter
            # Physically pauses the python execution thread to enforce backend throttling, 
            # rendering the LLM completely unable to forge a rapid-retry hallucination DDoS.
            time.sleep(5)
            
    try:
        yield
    finally:
        # Releasing the lock. 
        # (Note: Kernel natively releases it anyway on process OOM/Segfault)
        fcntl.flock(file_descriptor.fileno(), fcntl.LOCK_UN)
        file_descriptor.close()
