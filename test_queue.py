#!/usr/bin/env python3
"""
Test the queue-based worker function
"""
import multiprocessing as mp
import time

def _worker_main(job_q: mp.Queue, log_q: mp.Queue,
                 progress_q: mp.Queue):
    """Worker process that sends log messages via queue instead of pipe"""
    try:
        log_q.put("Worker process started!")
        log_q.put("Beginning progress simulation...")
        
        # Simulate work with progress updates
        for i in range(10):  # Shorter test
            progress_q.put(i + 1)
            
            # Send log messages periodically
            if i % 2 == 0:  # Log every 2 items
                log_q.put(f"Step {i+1}: Processing item {i+1}/10")
            
            time.sleep(0.5)  # Simulate work
        
        log_q.put("Worker process completed!")
        progress_q.put(None)  # Signal completion
        
    except Exception as e:
        log_q.put(f"Worker error: {e}")
        progress_q.put(None)  # Still signal completion

def main():
    mp.freeze_support()
    
    # Create queues
    job_q = mp.Queue()
    log_q = mp.Queue()
    progress_q = mp.Queue()
    
    # Start worker
    worker = mp.Process(target=_worker_main, args=(job_q, log_q, progress_q), daemon=True)
    worker.start()
    
    print("Main: Worker started, waiting for messages...")
    
    # Read messages
    while True:
        # Check for progress updates
        try:
            val = progress_q.get_nowait()
            if val is None:
                print("Main: Worker finished")
                break
            else:
                print(f"Main: Progress {val}")
        except Exception:
            pass
        
        # Check for log messages
        try:
            message = log_q.get_nowait()
            print(f"Main: Log: {message}")
        except Exception:
            pass
        
        time.sleep(0.1)
    
    worker.join(timeout=2)
    print("Main: Test completed")

if __name__ == "__main__":
    main()
