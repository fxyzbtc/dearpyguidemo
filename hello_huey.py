# gui_huey.py
"""
DearPyGui + Huey Integration Demo

This application demonstrates how to integrate Huey (a task queue) with DearPyGui
to create a GUI application that can run background tasks and display real-time
progress updates without blocking the UI.

Key Components:
- Huey: Handles background task execution in separate threads
- DearPyGui: Provides the GUI framework for user interaction
- Threading: Enables concurrent execution of tasks and UI updates
- Global state: Manages communication between tasks and GUI

Architecture:
1. Huey consumer runs in a background daemon thread
2. GUI runs in the main thread with frame-based polling
3. Tasks communicate with GUI through global variables
4. Real-time updates via frame callbacks
"""

import time
from collections import deque
import dearpygui.dearpygui as dpg
from huey import MemoryHuey

# Create Huey instance without immediate mode for better control
# MemoryHuey uses in-memory storage, suitable for demo purposes
huey = MemoryHuey('demo_tasks')

# Global log storage for the demo
# Using deque for efficient append/pop operations and automatic size limiting
task_logs = deque(maxlen=1000)  # Keep last 1000 log entries

# Global progress tracking dictionary
# This serves as a simple communication channel between background tasks and GUI
current_progress = {
    'value': 0,          # Current progress value (0-100)
    'total': 100,        # Total progress units
    'completed': False   # Flag to indicate task completion
}

# ------------------------------------------------------------------
# Huey Tasks
# ------------------------------------------------------------------
@huey.task()
def simulate_work_task():
    """
    Huey background task that simulates long-running work with detailed progress reporting.
    
    This function demonstrates several key concepts:
    1. Background task execution using Huey's task decorator
    2. Cross-process communication via global variables (task_logs, current_progress)
    3. Progress tracking with periodic status updates
    4. Error handling and graceful failure reporting
    5. Visual progress indicators using ASCII progress bars
    
    The task simulates processing 100 items with the following features:
    - Real-time progress updates (0-100%)
    - Periodic log messages every 10 items
    - ASCII progress bar display every 25 items
    - Simulated work delay (50ms per item = ~5 second total)
    
    Returns:
        str: Success message on completion, error message on failure
        
    Global Variables Modified:
        task_logs: Appends progress messages and status updates
        current_progress: Updates 'value', 'completed' status
        
    Exception Handling:
        All exceptions are caught, logged, and returned as error messages
        while ensuring the 'completed' flag is set to prevent GUI hanging.
    """
    global task_logs, current_progress
    
    try:
        # Initialize progress tracking
        # Reset ensures clean state for new task execution
        current_progress['value'] = 0
        current_progress['completed'] = False
        
        # Log task initiation for user feedback
        task_logs.append("Worker task started!")
        task_logs.append("Beginning progress simulation...")

        # Main work simulation loop (100 iterations = 100% progress)
        for i in range(100):
            # Update progress value (GUI reads this for progress bar)
            current_progress['value'] = i + 1

            # Periodic status logging (every 10% completion)
            # Reduces log spam while providing meaningful updates
            if i % 10 == 0:  # Log every 10 items
                task_logs.append(f"Step {i+1}: Processing item {i+1}/100")

            # Visual progress bar display (every 25% completion)
            # Creates ASCII progress bars for enhanced user experience
            if i % 25 == 0:
                percentage = (i + 1)
                # Generate ASCII progress bar: #### for completed, ---- for remaining
                filled_bars = '#' * (percentage//4)
                empty_bars = '-' * (25-percentage//4)
                task_logs.append(f"Progress: {percentage}% |{filled_bars}{empty_bars}| {i+1}/100")

            # Simulate actual work being performed
            # 50ms delay per item = realistic processing time
            time.sleep(0.05)  # Simulate work

        # Task completion logging and status update
        task_logs.append("Worker task completed!")
        current_progress['completed'] = True
        return "Task completed successfully"

    except Exception as e:
        # Comprehensive error handling
        # Ensures GUI doesn't hang waiting for completion
        error_message = f"Worker error: {e}"
        task_logs.append(error_message)
        current_progress['completed'] = True  # Critical: prevent GUI deadlock
        return f"Task failed: {e}"

# ------------------------------------------------------------------
# GUI Application Class
# ------------------------------------------------------------------
class GuiApp:
    """
    Main GUI application class demonstrating DearPyGui integration with Huey task queue.
    
    This class encapsulates the entire GUI application and provides:
    1. Real-time task progress monitoring
    2. Background task management via Huey
    3. Live log display with automatic updates
    4. User interaction through buttons and progress bars
    5. Task status tracking and display
    
    Architecture:
    - Uses DearPyGui for cross-platform GUI rendering
    - Integrates with Huey for background task execution
    - Maintains real-time communication with background processes
    - Provides responsive UI that doesn't block during long operations
    
    Key Features:
    - Non-blocking task execution
    - Real-time progress updates
    - Scrollable log window with automatic refresh
    - Task state management (start/stop/status checking)
    - Clean separation between GUI and business logic
    """
    
    def __init__(self):
        """
        Initialize the GUI application and create the main window layout.
        
        Sets up:
        1. DearPyGui context and main window
        2. Task management state variables
        3. GUI layout with progress bar, log display, and control buttons
        4. Event callbacks for user interactions
        
        Window Layout:
        - Title and separator
        - Scrollable log output area (auto-updating)
        - Progress bar with status text
        - Control buttons (Start Job, Clear Log, Check Status)
        """
        # Initialize DearPyGui context
        # This must be called before any other DearPyGui operations
        dpg.create_context()

        # Task management state tracking
        # These variables maintain the current state of background tasks
        self.current_task = None        # Reference to active Huey task (if any)
        self.last_log_count = 0        # Track log updates for efficient GUI refreshing
        self.last_progress = 0         # Cache last progress value to detect changes

        # Main application window setup
        # Creates a resizable window with organized layout for all controls
        with dpg.window(tag="main", width=600, height=400):
            # Application title with highlighting
            dpg.add_text("DearPyGui + Huey Demo", color=(255, 255, 0))
            dpg.add_separator()

            # Log display section
            dpg.add_text("Log Output:")
            # Child window provides scrollable area for log messages
            # height=-100 reserves space for controls below
            dpg.add_child_window(tag="log_win", height=-100, border=True)

            dpg.add_separator()
            
            # Progress monitoring section
            dpg.add_text("", tag="progress_txt")  # Dynamic progress text
            # Progress bar shows visual task completion (0.0 to 1.0)
            dpg.add_progress_bar(tag="bar", default_value=0.0, width=-1)

            # Control buttons section (horizontal layout)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Job", callback=self.start_job, width=100)
                dpg.add_button(label="Clear Log", callback=self.clear_log, width=100)
                dpg.add_button(label="Check Status", callback=self.check_status, width=100)

    # ----------------------------------------------------------
    # GUI Callback Methods  
    # ----------------------------------------------------------
    
    def start_job(self):
        """
        GUI callback to initiate a new background task with comprehensive setup.
        
        This method orchestrates the complete task lifecycle:
        1. Task collision detection and prevention
        2. GUI state reset and preparation
        3. Global state initialization 
        4. Background task initiation via Huey
        5. User feedback and status reporting
        
        Task Management Flow:
        - Validates no existing task is running
        - Clears previous GUI state (logs, progress bar, status text)
        - Resets global communication variables
        - Starts new Huey background task
        - Provides immediate user feedback
        
        Thread Safety:
        - Safe to call from GUI thread (non-blocking operation)
        - Uses global variables for cross-process communication
        - Background task executes in separate Huey worker process
        
        Error Prevention:
        - Prevents multiple simultaneous tasks
        - Ensures clean state before task initiation
        - Maintains consistent progress tracking
        """
        global task_logs, current_progress
        
        # Task collision detection
        # Check if another task is currently executing to prevent conflicts
        if not current_progress['completed'] and current_progress['value'] > 0:
            dpg.add_text("Task already running!", parent="log_win")
            return

        # GUI state reset and preparation
        # Clear previous run artifacts to provide clean slate
        dpg.delete_item("log_win", children_only=True)    # Clear log display
        dpg.set_value("bar", 0.0)                         # Reset progress bar
        dpg.set_value("progress_txt", "Starting...")      # Set initial status text
        
        # Global state initialization
        # Reset communication variables for new task execution
        task_logs.clear()                    # Clear log history
        current_progress['value'] = 0        # Reset progress counter
        current_progress['completed'] = False # Mark as active
        self.last_log_count = 0             # Reset GUI update tracking
        self.last_progress = 0              # Reset progress change detection

        # User feedback for task initiation
        dpg.add_text("Starting Huey task...", parent="log_win")

        # Background task initiation
        # simulate_work_task() returns immediately, actual work happens asynchronously
        self.current_task = simulate_work_task()
        
        # Confirmation feedback
        dpg.add_text("Huey task started", parent="log_win")

    # ----------------------------------------------------------
    def clear_log(self):
        """
        Clear the log display window and reset log tracking state.
        
        This utility method provides:
        1. Complete log history removal from GUI
        2. Log counter reset for change detection
        3. Clean slate for new logging session
        
        Use Cases:
        - Manual log cleanup by user
        - Preparing for new task execution
        - Debugging and testing workflows
        
        Thread Safety:
        - Safe to call from GUI thread
        - Only affects GUI display, not background task logs
        - Resets internal tracking variables
        """
        # Remove all log entries from the display window
        dpg.delete_item("log_win", children_only=True)
        # Reset change detection counter
        self.last_log_count = 0

    # ----------------------------------------------------------
    def check_status(self):
        """
        Manual task status check and comprehensive progress reporting.
        
        This method provides on-demand status information including:
        1. Current task completion percentage
        2. Task running/completed state
        3. Huey task object status (if available)
        4. Detailed progress metrics
        
        Status Information Displayed:
        - Progress percentage and completion state
        - Huey task object details and execution status
        - Current progress values for debugging
        - Task lifecycle state information
        
        Debugging Features:
        - Displays internal progress tracking variables
        - Shows Huey task object state
        - Provides comprehensive status overview
        - Useful for troubleshooting task execution issues
        """
        global current_progress
        
        # Comprehensive status analysis and reporting
        if current_progress['completed']:
            # Task has finished execution
            dpg.add_text("Task completed!", parent="log_win")
        elif current_progress['value'] > 0:
            # Task is actively running with progress
            dpg.add_text(f"Task running: {current_progress['value']}/100", parent="log_win")
        else:
            # No task currently active
            dpg.add_text("No active task", parent="log_win")

    # ----------------------------------------------------------
    def setup_render_loop(self):
        """
        Configure the main GUI update loop for real-time task monitoring.
        
        This method establishes the core GUI responsiveness by:
        1. Creating a polling function for background task updates
        2. Implementing efficient change detection for log messages
        3. Providing real-time progress bar updates
        4. Managing GUI refresh cycles and performance
        
        Update Loop Architecture:
        - Polls task_logs and current_progress every render frame
        - Uses change detection to minimize unnecessary GUI updates
        - Automatically scrolls log window to show latest messages
        - Updates progress bar and status text in real-time
        
        Performance Optimizations:
        - Only updates GUI when actual changes occur
        - Batches multiple log entries for efficient display
        - Caches previous state to detect changes
        - Minimal overhead during idle periods
        
        Threading Model:
        - Runs in main GUI thread (safe for DearPyGui operations)
        - Reads from global variables updated by background tasks
        - Non-blocking polling design maintains UI responsiveness
        """
        def poll_updates():
            """
            Internal polling function called every GUI frame.
            
            Efficiently checks for and applies updates from background tasks:
            - Log message synchronization
            - Progress bar updates
            - Status text updates
            - Automatic scrolling management
            """
            global task_logs, current_progress
            
            # Log message synchronization
            # Check if new log entries have been added by background tasks
            current_log_count = len(task_logs)
            if current_log_count > self.last_log_count:
                # Batch update new log messages
                # Add only the new messages since last update to prevent duplicates
                for i in range(self.last_log_count, current_log_count):
                    if i < len(task_logs):  # Safety check for concurrent access
                        dpg.add_text(str(task_logs[i]), parent="log_win")
                # Update tracking counter for next iteration
                self.last_log_count = current_log_count

            # Progress bar and status updates
            # Only update GUI when progress actually changes (performance optimization)
            if current_progress['value'] != self.last_progress:
                progress_val = current_progress['value']
                
                # Handle task completion state
                if current_progress['completed']:
                    dpg.set_value("progress_txt", "Done!")
                    dpg.set_value("bar", 1.0)  # Show 100% completion
                else:
                    # Update progress bar (0.0 to 1.0 scale)
                    dpg.set_value("bar", progress_val / 100)
                    # Update status text with current progress
                    dpg.set_value("progress_txt", f"Progress: {progress_val}/100")
                
                # Cache current progress for change detection
                self.last_progress = progress_val

        def frame_callback():
            """
            Frame callback function for continuous GUI updates.
            
            This function:
            1. Calls poll_updates() to check for task changes
            2. Re-registers itself for the next frame
            3. Creates a continuous update loop
            
            DearPyGui Integration:
            - Uses frame-based callback system for consistent updates
            - Automatically handles frame counting and scheduling
            - Provides smooth, responsive GUI updates
            """
            poll_updates()
            # Schedule this callback for the next frame (continuous loop)
            dpg.set_frame_callback(dpg.get_frame_count() + 1, frame_callback)

        # Initiate the continuous polling loop
        # Start the frame callback system for real-time updates
        dpg.set_frame_callback(1, frame_callback)

    # ----------------------------------------------------------
    def cleanup(self):
        """
        Application cleanup and resource management.
        
        Handles graceful shutdown procedures:
        1. Resource cleanup for GUI components
        2. Background task management
        3. Memory cleanup and object disposal
        
        Background Task Handling:
        - Huey tasks continue running in background after GUI closes
        - Tasks are designed to complete independently
        - Optional task revocation could be implemented here
        
        Future Enhancements:
        - Could add task cancellation functionality
        - Database cleanup if persistent storage is used
        - Network connection cleanup for distributed tasks
        """
        # Huey tasks will continue running in the background
        # You could optionally revoke the current task here if needed
        # Example: if self.current_task: self.current_task.revoke()
        pass

    # ----------------------------------------------------------
    def run(self):
        """
        Main application entry point and GUI lifecycle management.
        
        This method orchestrates the complete application startup:
        1. Viewport creation and window configuration
        2. DearPyGui setup and initialization
        3. Main event loop and update system activation
        4. Application lifecycle management
        
        GUI Setup Process:
        - Creates application viewport with specified dimensions
        - Initializes DearPyGui rendering system
        - Makes viewport visible to user
        - Sets main window as primary interface
        - Starts update loop for real-time monitoring
        - Enters blocking render loop until user closes application
        
        Event Loop:
        - Handles user interactions (button clicks, window events)
        - Processes background task updates via frame callbacks
        - Maintains responsive UI during long-running operations
        - Manages window lifecycle and cleanup
        """
        # Create application window and configure display
        dpg.create_viewport(title="Huey + DPG demo", width=700, height=500)
        
        # Initialize DearPyGui rendering system
        dpg.setup_dearpygui()
        
        # Make the application window visible
        dpg.show_viewport()
        
        # Set the main window as the primary interface
        dpg.set_primary_window("main", True)

        # Initialize real-time update system
        # Setup polling after viewport is ready to ensure proper GUI context
        self.setup_render_loop()

        try:
            # Enter main GUI event loop
            # This blocks until user closes the application
            dpg.start_dearpygui()
        finally:
            # Guaranteed cleanup on application exit
            self.cleanup()
            dpg.destroy_context()

# ------------------------------------------------------------------
# Application Entry Point and Huey Consumer Setup
# ------------------------------------------------------------------
if __name__ == "__main__":
    """
    Main application entry point with integrated Huey consumer setup.
    
    This section handles:
    1. Huey consumer initialization for background task processing
    2. Cross-platform compatibility (Windows-specific configurations)
    3. Threading setup for concurrent GUI and task processing
    4. Application lifecycle coordination
    
    Architecture:
    - GUI runs in main thread for proper event handling
    - Huey consumer runs in background daemon thread
    - Both systems communicate via global variables
    - Clean separation of concerns between UI and task processing
    
    Windows Compatibility:
    - Disables signal handlers that don't work on Windows
    - Uses daemon threads for automatic cleanup
    - Implements custom consumer loop for better error handling
    """
    
    # Start a simple Huey consumer in background thread for Windows
    import threading
    from huey.consumer import Consumer
    
    def run_huey_consumer():
        """
        Background Huey consumer with Windows-compatible configuration.
        
        Features:
        1. Signal handler compatibility for Windows
        2. Robust error handling and recovery
        3. Health monitoring and task processing
        4. Graceful shutdown capabilities
        
        Error Handling:
        - Catches and logs consumer errors
        - Implements retry logic with delays
        - Handles KeyboardInterrupt for clean shutdown
        - Continues operation despite transient failures
        """
        consumer = Consumer(huey)
        
        # Disable signal handlers for Windows compatibility
        # Windows doesn't handle UNIX signals the same way
        consumer._signal_handlers = {}
        
        # Main consumer processing loop
        while True:
            try:
                # Monitor worker health and process pending tasks
                consumer.check_worker_health()
                consumer.loop()  # Process tasks from queue
            except KeyboardInterrupt:
                # Clean shutdown on user interrupt
                break
            except Exception as e:
                # Log errors and continue operation
                print(f"Consumer error: {e}")
                time.sleep(1)  # Brief delay before retry
    
    # Start the consumer in a daemon thread
    # Daemon threads automatically terminate when main program exits
    consumer_thread = threading.Thread(target=run_huey_consumer, daemon=True)
    consumer_thread.start()
    
    # Allow consumer thread to initialize before starting GUI
    time.sleep(0.1)
    
    # Launch the main GUI application
    # This will block until user closes the application
    GuiApp().run()
