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
        print(f"Listening for connections on {host}:{port} for {server_name}...")


def handle_connection_test(server_name, client_socket, addr):
    print(f"Connection from {addr} to {server_name}")
    data = client_socket.recv(1024)
    if data:
        print(f"Received {len(data)} bytes from {addr}: {data}")

    if data.endswith(b'\xdd') or data.endswith(b'\x00'):
        print(f"{addr} is pinging the server.\n")
    else:
        print(f"{addr} is attempting to connect to the server.")


def handle_connection(server_name, client_socket, addr):
    print(f"Connection from {addr} to {server_name}")
    data = client_socket.recv(1024)
    if data:
        print(f"Recieved {len(data)} bytes from {addr}: {data}")
    if data.endswith(b'\xdd') or data.endswith(b'\x00'):
        print(f"{addr} is pinging {server_name}\n")
        return
    else:
        print(f"{addr} is attempting to connect to {server_name}")
        print(f"Starting {server_name}")
        try:
            server_info = socket_servers[server_name]
            session_name = f"{server_name}"
            print(f"The current session is {session_name}")
            tmux_session_cmd = f"tmux new-session -d -s {server_name}"
            tmux_send_keys_cmd = f"tmux send-keys -t {session_name} 'cd {server_info['starup_script']} && {server_info['startup_program']}' Enter"

            print(f"Excecuting command: {tmux_session_cmd}\n")
            subprocess.run(tmux_session_cmd, shell=True, check=True)

            print(f"Excecuting command: {tmux_send_keys_cmd}\n")
            subprocess.run(tmux_send_keys_cmd, shell=True, check=True)

            last_activity[server_name] = time.time()
            socket_servers[server_name]['running'] = True

            # Close client socket before server finished starting
            client_socket.close()
            socket_servers[server_name]['server_socket'].close()
            print(f"Client and server sockets closed after starting {server_name}")
        except Exception as error:
            print(f"Error starting {server_name}: {error}")
            
        time.sleep(5)
        log_file = server_info['log_file']
        print(f"Log file location is {log_file}")
        if os.path.exists(log_file):
            threading.Thread(target=follow_log, args=(server_name, log_file), daemon=True).start()
        else:
            print(f"Log file {log_file} not found for {server_name}. Monitoring not started.")


def stop_server(server_name):
    cmd = f"tmux send-keys -t {server_name} /stop Enter"
    subprocess.run(cmd, shell=True)
    time.speep(5)
    monitoring[server_name] = False
    socket_servers[server_name]['running'] = False
    cmd = f"tmux kill-session -t {server_name}"
    subprocess.rum(cmd, shell = True)
    socket_servers[server_name]['server_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    socket_servers[server_name]['server_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0)) 
    socket_servers[server_name]['server_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    socket_servers[server_name]['server_socket'].bind((SERVER_CONFIGS[server_name]['host'], SERVER_CONFIGS[server_name]['port'])) 
    socket_servers[server_name]['server_socket'].listen(5) 
    socket_servers[server_name]['server_socket'].setblocking(0)
    last_activity[server_name] = time.time()
