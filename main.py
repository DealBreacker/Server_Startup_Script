# main.py
import time
import socket
import threading
import os
from datetime import datetime
from server_configs import last_activity, players_online, SERVER_CONFIGS
from server_management import socket_servers, handle_connection, stop_server, setup_server_sockets
from tmux_manager import kill_tmux_sessions
from logging_system import initialize_log_files, log_connection, generate_daily_summary, save_state, load_state, rollover_server_logs, rollover_summary_logs
from shutdown_manager import stop_signal, check_for_stop, stop_all_servers, close_all_threads, log_shutdown_event, input_listener

DEBUG_MODE = 0  # Set to 1 for debugging (only print information), 0 for normal operation

def main():
    # Ensure log directories exist
    os.makedirs("summary_logs", exist_ok=True)
    os.makedirs("server_logs", exist_ok=True)

    if DEBUG_MODE:
        print("Debug Mode Active: No servers will be started.")
    else:
        kill_tmux_sessions()  # Ensuring tmux sessions are killed before starting the servers
        setup_server_sockets()  # Initializing the server sockets
    
    initialize_log_files(SERVER_CONFIGS.keys())

    # Load saved state if it exists
    loaded_players_online, loaded_last_activity = load_state()
    if loaded_players_online and loaded_last_activity:
        players_online.update(loaded_players_online)
        last_activity.update(loaded_last_activity)

    # Start the input thread
    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()

    print("Type '/stop' and press Enter at any time to stop the program.")

    last_day = datetime.now().day
    last_save = time.time()
    last_print = time.time()
    print_interval = 10  # Print every 10 seconds
    loop_count = 0

    while not stop_signal.is_set():
        if check_for_stop():
            break

        loop_count += 1
        current_time = datetime.now()

        if time.time() - last_print >= print_interval:
            print(f"Current time is {current_time.strftime('%Y/%m/%d %H:%M:%S')}")
            for server_name, last_time in last_activity.items():
                if DEBUG_MODE:
                    print(f"Checking activity for {server_name}: Last activity at {datetime.fromtimestamp(last_time).strftime('%Y/%m/%d %H:%M:%S')}")
            last_print = time.time()
        
        if current_time.day != last_day:
            generate_daily_summary()
            last_day = current_time.day
            # Rollover logs for all servers
            for server_name in SERVER_CONFIGS.keys():
                rollover_server_logs(server_name)
        
        # Save state every 5 minutes
        if time.time() - last_save > 300:
            save_state(players_online, last_activity)
            last_save = time.time()

        for server_name, info in socket_servers.items():
            server_socket = info['server_socket']
            try:
                if not DEBUG_MODE:
                    client_socket, addr = server_socket.accept()
                    client_socket.settimeout(2)
                    handle_connection(server_name, client_socket, addr)
                    log_connection(server_name, "connection", addr)
                    client_socket.close()
            except socket.error:
                pass

            # Check activity every 0.1 seconds, but only act on it
            if not DEBUG_MODE and socket_servers[server_name]['running'] and time.time() - last_activity[server_name] > 1800 and not players_online[server_name]:
                stop_server(server_name)

        time.sleep(0.1)  # Sleep for 1/10 of a second

    print("Stop signal received. Initiating shutdown...")
    stop_all_servers(socket_servers, stop_server)
    close_all_threads()
    log_shutdown_event()
    print("Shutdown complete.")

if __name__ == "__main__":
    main()
