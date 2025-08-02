# gui_mp.py
import threading
import queue
import time
import dearpygui.dearpygui as dpg

# ------------------------------------------------------------------
# Worker Thread
# ------------------------------------------------------------------
def worker_thread(job_q: queue.Queue, log_q: queue.Queue, progress_q: queue.Queue):
    """Worker thread that sends log messages via queue"""
    try:
        log_q.put("Worker thread started!")
        log_q.put("Beginning progress simulation...")

        # Simulate work with progress updates
        for i in range(100):
            progress_q.put(i + 1)

            time.sleep(0.05)  # Simulate work

        log_q.put("Worker thread completed!")
        progress_q.put(None)  # Signal completion

    except Exception as e:
        log_q.put(f"Worker error: {e}")
        progress_q.put(None)  # Still signal completion

# ------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------
class GuiApp:
    def __init__(self):
        dpg.create_context()

        # queues
        self.job_q = queue.Queue()
        self.progress_q = queue.Queue()
        self.log_q = queue.Queue()

        # widgets
        with dpg.window(tag="main", width=600, height=400):
            dpg.add_text("DearPyGui + Threading Demo", color=(255, 255, 0))
            dpg.add_separator()

            dpg.add_text("Log Output:")
            dpg.add_child_window(tag="log_win", height=-100, border=True)

            dpg.add_separator()
            dpg.add_text("", tag="progress_txt")
            dpg.add_progress_bar(tag="bar", default_value=0.0, width=-1)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Job", callback=self.start_job, width=100)
                dpg.add_button(label="Clear Log", callback=self.clear_log, width=100)

        # polling state
        self.worker_thread = None

    # ----------------------------------------------------------
    def start_job(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return

        # Clear any remaining items in the queues
        while not self.progress_q.empty():
            try:
                self.progress_q.get_nowait()
            except Exception:
                break

        while not self.log_q.empty():
            try:
                self.log_q.get_nowait()
            except Exception:
                break

        # reset UI
        dpg.set_value("bar", 0.0)
        dpg.set_value("progress_txt", "Starting...")
        dpg.delete_item("log_win", children_only=True)

        # Add initial debug message
        dpg.add_text("Spawning worker thread...", parent="log_win")

        # spawn worker
        self.worker_thread = threading.Thread(
            target=worker_thread,
            args=(self.job_q, self.log_q, self.progress_q),
            daemon=True)
        self.worker_thread.start()

        # Confirm worker started
        dpg.add_text("Worker thread started", parent="log_win")

    # ----------------------------------------------------------
    def clear_log(self):
        """Clear the log window"""
        dpg.delete_item("log_win", children_only=True)

    # ----------------------------------------------------------
    def setup_render_loop(self):
        # poll progress
        def poll_progress():
            try:
                val = self.progress_q.get_nowait()
                if val is None:                       # finished
                    dpg.set_value("progress_txt", "Done!")
                    dpg.set_value("bar", 1.0)
                else:
                    dpg.set_value("bar", val / 100)
                    dpg.set_value("progress_txt", f"Progress: {val}/100")
            except Exception:
                pass

        # poll log lines
        def poll_log():
            try:
                # Process multiple log messages per frame for better responsiveness
                for _ in range(10):  # Process up to 10 messages per frame
                    try:
                        message = self.log_q.get_nowait()
                        dpg.add_text(str(message), parent="log_win")
                    except Exception:
                        break  # No more messages
            except Exception as e:
                dpg.add_text(f"Log polling error: {e}", parent="log_win")

        def frame_callback():
            poll_progress()
            poll_log()
            # Re-register the callback for the next frame to create continuous polling
            dpg.set_frame_callback(dpg.get_frame_count() + 1, frame_callback)

        # Start the continuous polling loop
        dpg.set_frame_callback(1, frame_callback)

    # ----------------------------------------------------------
    def cleanup(self):
        """Clean up resources when closing the application"""
        # Threads don't need explicit termination like processes
        pass

    # ----------------------------------------------------------
    def run(self):
        dpg.create_viewport(title="Threading + DPG demo", width=700, height=500)
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
    GuiApp().run()
