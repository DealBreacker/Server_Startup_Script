# server_management.py
import socket, socket, subprocess, time, threading, os, struct
from server_configs import SERVER_CONFIGS, last_activity, monitoring
from log_monitoring import follow_log

socket_servers = {}

def setup_server_sockets():
    for server_name, config in SERVER_CONFIGS.items():
        host = config['host']
        port = config['port']  # Changed from 'host' to 'port'
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.setblocking(0)
        socket_servers[server_name] = {
            'server_socket': server_socket,  # Changed from 'startup_socket' to 'server_socket'
            'startup_script': config['startup_script'],
            'startup_program': config['startup_program'],
            'log_file': config['log_file'],
            'running': False
        }
        print(f"\nListening for connections on {host}:{port} for {server_name}...")


def handle_connection_test(server_name, client_socket, addr):
    print(f"Connection from {addr} to {server_name}")
    try:
        data = client_socket.recv(1024)
        if data:
            print(f"Received {len(data)} bytes from {addr}: {data}")
            
            # Check for various ping patterns
            if (data.endswith(b'\xdd\x01\x01\x00') or
                data.endswith(b'\x00c\xdd') or
                b'\x00M\x00C\x00|\x00P\x00i\x00n\x00g\x00H\x00o\x00s\x00t' in data or
                (data[0] in [0x1a, 0x1e, 0x21, 0x24] and b'\xff\x05' in data[:5])):
                print(f"{addr} is pinging the server {server_name}.")
            else:
                print(f"{addr} is attempting to connect to the server {server_name}.")
        else:
            print(f"No data received from {addr}.")
    except socket.error as e:
        print(f"Error receiving data from {addr}: {e}")
    finally:
        client_socket.close()


def handle_connection(server_name, client_socket, addr):
    print(f"Connection from {addr} to {server_name}")
    try:
        data = client_socket.recv(1024)
        if data:
            print(f"Received {len(data)} bytes from {addr}: {data}")
            
            # Check for various ping patterns
            if (data.endswith(b'\xdd\x01\x01\x00') or
                data.endswith(b'\x00c\xdd') or
                b'\x00M\x00C\x00|\x00P\x00i\x00n\x00g\x00H\x00o\x00s\x00t' in data or
                (len(data) < 50 and data[0] in [0x1a, 0x1e, 0x21, 0x24] and b'\xff\x05' in data[:5])):
                print(f"{addr} is pinging the server {server_name}")
                return
            else:
                print(f"{addr} is attempting to connect to {server_name}")
                # Start server logic here
                server_info = socket_servers[server_name]
                session_name = f"{server_name}"
                print(f"The current session is {session_name}")
                tmux_session_cmd = f"tmux new-session -d -s {server_name}"
                tmux_send_keys_cmd = f"tmux send-keys -t {session_name} 'cd {server_info['startup_script']} && {server_info['startup_program']}' Enter"

                print(f"Executing command: {tmux_session_cmd}")
                subprocess.run(tmux_session_cmd, shell=True, check=True)

                print(f"Executing command: {tmux_send_keys_cmd}")
                subprocess.run(tmux_send_keys_cmd, shell=True, check=True)

                last_activity[server_name] = time.time()
                socket_servers[server_name]['running'] = True

                # Close client socket before server finished starting
                client_socket.close()
                socket_servers[server_name]['server_socket'].close()
                print(f"Client and server sockets closed after starting {server_name}")

                time.sleep(5)
                log_file = server_info['log_file']
                print(f"Log file location is {log_file}")
                if os.path.exists(log_file):
                    threading.Thread(target=follow_log, args=(server_name, log_file), daemon=True).start()
                    print(f"Log file {log_file} is currently being tracked for {server_name}, monitoring started")
                else:
                    print(f"Log file {log_file} not found for {server_name}. Monitoring not started.")
        else:
            print(f"No data received from {addr}")
    except Exception as error:
        print(f"Error handling connection for {server_name}: {error}")
    finally:
        client_socket.close()


def stop_server(server_name):
    cmd = f"tmux send-keys -t {server_name} /stop Enter"
    subprocess.run(cmd, shell=True)
    time.sleep(5)
    monitoring[server_name] = False
    socket_servers[server_name]['running'] = False
    cmd = f"tmux kill-session -t {server_name}"
    subprocess.run(cmd, shell = True)
    socket_servers[server_name]['server_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    socket_servers[server_name]['server_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0)) 
    socket_servers[server_name]['server_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    socket_servers[server_name]['server_socket'].bind((SERVER_CONFIGS[server_name]['host'], SERVER_CONFIGS[server_name]['port'])) 
    socket_servers[server_name]['server_socket'].listen(5) 
    socket_servers[server_name]['server_socket'].setblocking(0)
    last_activity[server_name] = time.time()
