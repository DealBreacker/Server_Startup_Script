# main.py
import time
import socket
from datetime import datetime
from server_configs import last_activity, players_online, SERVER_CONFIGS
from server_management import socket_servers, handle_connection, stop_server, setup_server_sockets
from tmux_manager import kill_tmux_sessions
from logging_system import initialize_log_files, log_connection, generate_daily_summary

DEBUG_MODE = 1  # Set to 1 for debugging (only print information), 0 for normal operation

def main():
    if DEBUG_MODE:
        print("Debug Mode Active: No servers will be started.")
    else:
        kill_tmux_sessions()  # Ensuring tmux sessions are killed before starting the servers
        setup_server_sockets()  # Initializing the server sockets
    
    initialize_log_files(SERVER_CONFIGS.keys())

    last_day = datetime.now().day
    while True:
        current_time = datetime.now()
        print(f"Current time is {current_time.strftime('%Y/%m/%d %H:%M:%S')}")
        
        if current_time.day != last_day:
            generate_daily_summary()
            last_day = current_time.day
        
        for server_name, info in socket_servers.items():
            server_socket = info['server_socket']
            try:
                if DEBUG_MODE:
                    print(f"Would handle connection for {server_name} at {server_socket.getsockname()}")
                else:
                    client_socket, addr = server_socket.accept()
                    client_socket.settimeout(2)
                    handle_connection(server_name, client_socket, addr)
                    log_connection(server_name, "connection", addr)
                    client_socket.close()
            except socket.error:
                pass
        for server_name, last_time in last_activity.items():
            if DEBUG_MODE:
                print(f"Checking activity for {server_name}: Last activity at {datetime.fromtimestamp(last_time).strftime('%Y/%m/%d %H:%M:%S')}")
            else:
                if socket_servers[server_name]['running'] and time.time() - last_time > 900 and not players_online[server_name]:
                    stop_server(server_name)
        time.sleep(1)

if __name__ == "__main__":
    main()
