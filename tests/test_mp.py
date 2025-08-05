#!/usr/bin/env python3
"""
Simple test to verify multiprocessing and pipe communication works
"""
import multiprocessing as mp
from multiprocessing.connection import Connection
import sys
import time
import io

def worker_test(log_w: Connection, progress_q: mp.Queue):
    """Simple worker that sends messages through pipe"""
    try:
        # Redirect stdout to pipe
        class _PipeWriter(io.RawIOBase):
            def __init__(self, pipe):
                self.pipe = pipe
            
            def write(self, b):
                try:
                    if isinstance(b, str):
                        b = b.encode('utf-8')
                    self.pipe.send_bytes(b)
                    return len(b)
                except (BrokenPipeError, ConnectionError):
                    return 0
            
            def writable(self):
                return True
            
            def readable(self):
                return False
        
        sys.stdout = io.TextIOWrapper(_PipeWriter(log_w), line_buffering=True)
        
        print("Worker started!")
        for i in range(5):
            print(f"Message {i+1}")
            progress_q.put(i + 1)
            time.sleep(1)
        
        print("Worker finished!")
        progress_q.put(None)
        
    except Exception as e:
        print(f"Worker error: {e}")
    finally:
        try:
            log_w.close()
        except Exception:
            pass

def main():
    mp.freeze_support()
    
    # Create communication objects
    progress_q = mp.Queue()
    log_r, log_w = mp.Pipe(duplex=False)
    
    # Start worker
    worker = mp.Process(target=worker_test, args=(log_w, progress_q), daemon=True)
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
        if log_r.poll(0.1):
            try:
                data = log_r.recv_bytes()
                message = data.decode('utf-8', errors='replace').strip()
                print(f"Main: Log received: '{message}'")
            except EOFError:
                print("Main: Log pipe closed")
                break
            except Exception as e:
                print(f"Main: Log error: {e}")
        
        time.sleep(0.1)
    
    worker.join(timeout=2)
    log_r.close()
    print("Main: Test completed")

if __name__ == "__main__":
    main()
