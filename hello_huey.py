# gui_huey.py
import time
from collections import deque
import dearpygui.dearpygui as dpg
from huey import MemoryHuey

# Create Huey instance without immediate mode
huey = MemoryHuey('demo_tasks')

# Global log storage for the demo
task_logs = deque(maxlen=1000)  # Keep last 1000 log entries
current_progress = {'value': 0, 'total': 100, 'completed': False}

# ------------------------------------------------------------------
# Huey Tasks
# ------------------------------------------------------------------
@huey.task()
def simulate_work_task():
    """Huey task that simulates work with progress updates"""
    global task_logs, current_progress
    
    try:
        # Reset progress
        current_progress['value'] = 0
        current_progress['completed'] = False
        
        task_logs.append("Worker task started!")
        task_logs.append("Beginning progress simulation...")

        # Simulate work with progress updates
        for i in range(100):
            current_progress['value'] = i + 1

            # Send log messages periodically
            if i % 10 == 0:  # Log every 10 items
                task_logs.append(f"Step {i+1}: Processing item {i+1}/100")

            # Send tqdm-style progress occasionally
            if i % 25 == 0:
                percentage = (i + 1)
                task_logs.append(f"Progress: {percentage}% |{'#' * (percentage//4)}{'-' * (25-percentage//4)}| {i+1}/100")

            time.sleep(0.05)  # Simulate work

        task_logs.append("Worker task completed!")
        current_progress['completed'] = True
        return "Task completed successfully"

    except Exception as e:
        task_logs.append(f"Worker error: {e}")
        current_progress['completed'] = True
        return f"Task failed: {e}"

# ------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------
class GuiApp:
    def __init__(self):
        dpg.create_context()

        # Task management
        self.current_task = None
        self.last_log_count = 0
        self.last_progress = 0

        # widgets
        with dpg.window(tag="main", width=600, height=400):
            dpg.add_text("DearPyGui + Huey Demo", color=(255, 255, 0))
            dpg.add_separator()

            dpg.add_text("Log Output:")
            dpg.add_child_window(tag="log_win", height=-100, border=True)

            dpg.add_separator()
            dpg.add_text("", tag="progress_txt")
            dpg.add_progress_bar(tag="bar", default_value=0.0, width=-1)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Job", callback=self.start_job, width=100)
                dpg.add_button(label="Clear Log", callback=self.clear_log, width=100)
                dpg.add_button(label="Check Status", callback=self.check_status, width=100)

    # ----------------------------------------------------------
    def start_job(self):
        global task_logs, current_progress
        
        # Simple check if task is running by checking our progress state
        if not current_progress['completed'] and current_progress['value'] > 0:
            dpg.add_text("Task already running!", parent="log_win")
            return

        # Clear log display and reset progress
        dpg.delete_item("log_win", children_only=True)
        dpg.set_value("bar", 0.0)
        dpg.set_value("progress_txt", "Starting...")
        
        # Clear global logs and reset progress
        task_logs.clear()
        current_progress['value'] = 0
        current_progress['completed'] = False
        self.last_log_count = 0
        self.last_progress = 0

        # Add initial debug message
        dpg.add_text("Starting Huey task...", parent="log_win")

        # Start the task - this will run in a background thread
        self.current_task = simulate_work_task()
        
        dpg.add_text("Huey task started", parent="log_win")

    # ----------------------------------------------------------
    def clear_log(self):
        """Clear the log window"""
        dpg.delete_item("log_win", children_only=True)
        self.last_log_count = 0

    # ----------------------------------------------------------
    def check_status(self):
        """Manually check task status"""
        global current_progress
        if current_progress['completed']:
            dpg.add_text("Task completed!", parent="log_win")
        elif current_progress['value'] > 0:
            dpg.add_text(f"Task running: {current_progress['value']}/100", parent="log_win")
        else:
            dpg.add_text("No active task", parent="log_win")

    # ----------------------------------------------------------
    def setup_render_loop(self):
        def poll_updates():
            global task_logs, current_progress
            
            # Poll for new log messages
            current_log_count = len(task_logs)
            if current_log_count > self.last_log_count:
                # Add new log messages
                for i in range(self.last_log_count, current_log_count):
                    if i < len(task_logs):
                        dpg.add_text(str(task_logs[i]), parent="log_win")
                self.last_log_count = current_log_count

            # Poll for progress updates
            if current_progress['value'] != self.last_progress:
                progress_val = current_progress['value']
                if current_progress['completed']:
                    dpg.set_value("progress_txt", "Done!")
                    dpg.set_value("bar", 1.0)
                else:
                    dpg.set_value("bar", progress_val / 100)
                    dpg.set_value("progress_txt", f"Progress: {progress_val}/100")
                self.last_progress = progress_val

        def frame_callback():
            poll_updates()
            # Re-register the callback for the next frame to create continuous polling
            dpg.set_frame_callback(dpg.get_frame_count() + 1, frame_callback)

        # Start the continuous polling loop
        dpg.set_frame_callback(1, frame_callback)

    # ----------------------------------------------------------
    def cleanup(self):
        """Clean up resources when closing the application"""
        # Huey tasks will continue running in the background
        # You could optionally revoke the current task here if needed
        pass

    # ----------------------------------------------------------
    def run(self):
        dpg.create_viewport(title="Huey + DPG demo", width=700, height=500)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)

        # Set up polling after viewport is ready
        self.setup_render_loop()

        try:
            dpg.start_dearpygui()
        finally:
            self.cleanup()
            dpg.destroy_context()

# ------------------------------------------------------------------
if __name__ == "__main__":
    # Start a simple Huey consumer in background thread for Windows
    import threading
    from huey.consumer import Consumer
    
    def run_huey_consumer():
        """Run Huey consumer with signal handling disabled for Windows compatibility"""
        consumer = Consumer(huey)
        # Disable signal handlers for Windows compatibility
        consumer._signal_handlers = {}
        
        # Simple consumer loop
        while True:
            try:
                consumer.check_worker_health()
                consumer.loop()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Consumer error: {e}")
                time.sleep(1)
    
    # Start the consumer in a daemon thread
    consumer_thread = threading.Thread(target=run_huey_consumer, daemon=True)
    consumer_thread.start()
    
    # Give the consumer a moment to start
    time.sleep(0.1)
    
    # Run the GUI
    GuiApp().run()
