# shutdown_manager.py
import threading
from datetime import datetime
import queue, os

stop_signal = threading.Event()
input_queue = queue.Queue()

def input_listener():
    while not stop_signal.is_set():
        try:
            input_line = input()
            input_queue.put(input_line)
        except EOFError:
            # This can happen if the input stream is closed
            break

def check_for_stop():
    try:
        user_input = input_queue.get_nowait()
        if user_input.strip().lower() == "/stop":
            stop_signal.set()
            print("\nStop command received. Shutting down...")
            return True
    except queue.Empty:
        pass
    return False

def stop_all_servers(socket_servers, stop_server_func):
    print("Stopping all servers...")
    for server_name, info in socket_servers.items():
        if info['running']:
            stop_server_func(server_name)
    print("All servers stopped.")

def close_all_threads():
    print("Closing all threads...")
    # Add code to close any other threads you've created
    print("All threads closed.")

def log_shutdown_event():
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join("summary_logs", f"{current_date}_summary.log")
    current_time = datetime.now().strftime('%H:%M:%S')
    
    with open(log_file, 'a') as f:
        f.write(f"{current_time} - Shutdown event: All servers and threads stopped.\n")

