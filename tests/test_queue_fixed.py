#!/usr/bin/env python3
"""
Test the queue-based worker function
"""
import multiprocessing as mp
import time
import queue

def _worker_main(job_q: mp.Queue, log_q: mp.Queue, progress_q: mp.Queue):
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
            
            time.sleep(0.1)  # Reduced sleep time for faster tests
        
        log_q.put("Worker process completed!")
        progress_q.put(None)  # Signal completion
        
    except Exception as e:
        log_q.put(f"Worker error: {e}")
        progress_q.put(None)  # Still signal completion

def _worker_with_error(job_q: mp.Queue, log_q: mp.Queue, progress_q: mp.Queue):
    """Worker that raises an exception for testing error handling"""
    try:
        log_q.put("Worker starting...")
        time.sleep(0.1)  # Give time for message to be sent
        raise ValueError("Test error")
    except Exception as e:
        log_q.put(f"Worker error: {e}")
        progress_q.put(None)  # Signal completion even on error

def _worker_immediate_exit(job_q: mp.Queue, log_q: mp.Queue, progress_q: mp.Queue):
    """Worker that exits immediately"""
    log_q.put("Worker immediate exit")
    time.sleep(0.1)  # Give time for message to be sent
    progress_q.put(None)

class TestQueueWorker:
    
    def test_worker_main_success(self):
        """Test successful worker execution"""
        if mp.get_start_method(allow_none=True) != 'spawn':
            mp.set_start_method('spawn', force=True)
        
        job_q = mp.Queue()
        log_q = mp.Queue()
        progress_q = mp.Queue()
        
        worker = mp.Process(target=_worker_main, args=(job_q, log_q, progress_q))
        worker.start()
        
        progress_values = []
        log_messages = []
        
        # Collect messages with timeout
        start_time = time.time()
        while time.time() - start_time < 5:  # Reduced timeout
            try:
                val = progress_q.get(timeout=0.1)
                if val is None:
                    break
                progress_values.append(val)
            except queue.Empty:
                pass
            
            # Collect all available log messages
            while True:
                try:
                    message = log_q.get_nowait()
                    log_messages.append(message)
                except queue.Empty:
                    break
        
        # Get any remaining log messages
        worker.join(timeout=2)
        while True:
            try:
                message = log_q.get_nowait()
                log_messages.append(message)
            except queue.Empty:
                break
        
        # Assertions
        assert len(progress_values) == 10
        assert progress_values == list(range(1, 11))
        assert len(log_messages) >= 6  # At least start, begin, some steps, complete
        assert "Worker process started!" in log_messages
        assert "Worker process completed!" in log_messages
    
    def test_worker_error_handling(self):
        """Test worker error handling"""
        if mp.get_start_method(allow_none=True) != 'spawn':
            mp.set_start_method('spawn', force=True)
        
        job_q = mp.Queue()
        log_q = mp.Queue()
        progress_q = mp.Queue()
        
        worker = mp.Process(target=_worker_with_error, args=(job_q, log_q, progress_q))
        worker.start()
        
        log_messages = []
        completion_signal = False
        
        start_time = time.time()
        while time.time() - start_time < 3:
            try:
                val = progress_q.get(timeout=0.1)
                if val is None:
                    completion_signal = True
                    break
            except queue.Empty:
                pass
            
            try:
                message = log_q.get_nowait()
                log_messages.append(message)
            except queue.Empty:
                pass
        
        worker.join(timeout=2)
        
        # Get any remaining messages
        while True:
            try:
                message = log_q.get_nowait()
                log_messages.append(message)
            except queue.Empty:
                break
        
        # Should receive error message and completion signal
        assert completion_signal
        assert any("Worker error:" in msg for msg in log_messages)
    
    def test_worker_immediate_exit(self):
        """Test worker that exits immediately"""
        if mp.get_start_method(allow_none=True) != 'spawn':
            mp.set_start_method('spawn', force=True)
        
        job_q = mp.Queue()
        log_q = mp.Queue()
        progress_q = mp.Queue()
        
        worker = mp.Process(target=_worker_immediate_exit, args=(job_q, log_q, progress_q))
        worker.start()
        
        completion_signal = False
        log_messages = []
        
        start_time = time.time()
        while time.time() - start_time < 2:
            try:
                val = progress_q.get(timeout=0.1)
                if val is None:
                    completion_signal = True
                    break
            except queue.Empty:
                pass
            
            try:
                message = log_q.get_nowait()
                log_messages.append(message)
            except queue.Empty:
                pass
        
        worker.join(timeout=1)
        
        # Get any remaining messages
        while True:
            try:
                message = log_q.get_nowait()
                log_messages.append(message)
            except queue.Empty:
                break
        
        assert completion_signal
        assert "Worker immediate exit" in log_messages
    
    def test_queue_creation(self):
        """Test queue creation and basic operations"""
        job_q = mp.Queue()
        log_q = mp.Queue()
        progress_q = mp.Queue()
        
        # Test putting and getting items
        test_item = "test message"
        log_q.put(test_item)
        retrieved = log_q.get(timeout=1)
        
        assert retrieved == test_item
    
    def test_multiple_workers(self):
        """Test multiple workers running concurrently"""
        if mp.get_start_method(allow_none=True) != 'spawn':
            mp.set_start_method('spawn', force=True)
        
        num_workers = 2
        workers = []
        queues = []
        
        for i in range(num_workers):
            job_q = mp.Queue()
            log_q = mp.Queue()
            progress_q = mp.Queue()
            queues.append((job_q, log_q, progress_q))
            
            worker = mp.Process(target=_worker_immediate_exit, args=(job_q, log_q, progress_q))
            workers.append(worker)
            worker.start()
        
        # Wait for all workers to complete
        completed_workers = 0
        start_time = time.time()
        
        while completed_workers < num_workers and time.time() - start_time < 5:
            for i, (job_q, log_q, progress_q) in enumerate(queues):
                try:
                    val = progress_q.get_nowait()
                    if val is None:
                        completed_workers += 1
                except queue.Empty:
                    pass
            time.sleep(0.1)
        
        for worker in workers:
            worker.join(timeout=1)
        
        assert completed_workers == num_workers
    
    def test_queue_timeout(self):
        """Test queue timeout behavior"""
        test_queue = mp.Queue()
        
        # Test timeout on empty queue
        try:
            test_queue.get(timeout=0.1)
            assert False, "Should have raised queue.Empty"
        except queue.Empty:
            pass  # Expected
    
    def test_queue_put_get_multiple_items(self):
        """Test putting and getting multiple items"""
        test_queue = mp.Queue()
        test_items = ["item1", "item2", "item3"]
        
        # Put all items
        for item in test_items:
            test_queue.put(item)
        
        # Get all items
        retrieved_items = []
        for _ in range(len(test_items)):
            retrieved_items.append(test_queue.get(timeout=1))
        
        assert retrieved_items == test_items

def main():
    """Main function to run tests manually"""
    if mp.get_start_method(allow_none=True) != 'spawn':
        mp.set_start_method('spawn', force=True)
    
    print("Running queue tests...")
    test_worker = TestQueueWorker()
    
    try:
        test_worker.test_queue_creation()
        print("✓ Queue creation test passed")
        
        test_worker.test_queue_timeout()
        print("✓ Queue timeout test passed")
        
        test_worker.test_queue_put_get_multiple_items()
        print("✓ Queue multiple items test passed")
        
        print("All basic tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()
