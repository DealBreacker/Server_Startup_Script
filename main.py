# main.py
import time
import socket
from server_configs import last_activity, players_online
from server_management import socket_servers, handle_connection, stop_server, setup_server_sockets
from tmux_manager import kill_tmux_sessions

DEBUG_MODE = 1  # Set to 1 for debugging (only print information), 0 for normal operation

def main():
    if DEBUG_MODE:
        print("Debug Mode Active: No servers will be started.")
    else:
        kill_tmux_sessions()  # Ensuring tmux sessions are killed before starting the servers
        setup_server_sockets()  # Initializing the server sockets

    while True:
        current_time = time.time()
        print(f"Current time is {current_time}")
        for server_name, info in socket_servers.items():
            server_socket = info['server_socket']
            try:
                if DEBUG_MODE:
                    print(f"Would handle connection for {server_name} at {server_socket.getsockname()}")
                else:
                    client_socket, addr = server_socket.accept()
                    client_socket.settimeout(2)
                    handle_connection(server_name, client_socket, addr)
                    client_socket.close()
            except socket.error:
                pass
        for server_name, last_time in last_activity.items():
            if DEBUG_MODE:
                print(f"Checking activity for {server_name}: Last activity at {last_time}")
            else:
                if socket_servers[server_name]['running'] and time.time() - last_time > 1800 and not players_online[server_name]:
                    stop_server(server_name)
        time.sleep(1)

if __name__ == "__main__":
    main()
