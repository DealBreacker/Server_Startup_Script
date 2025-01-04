import os
from datetime import datetime, timedelta

def initialize_log_files(server_names):
    for server in server_names:
        player_log_file = f"{server}-player_logs.txt"
        if not os.path.exists(player_log_file):
            open(player_log_file, 'w').close()

def update_player_log(server_name, player_name, action, duration=None):
    log_file = f"{server_name}-player_logs.txt"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        player_found = False
        for line in lines:
            if line.startswith(player_name + ','):
                parts = line.strip().split(',')
                if action == 'join':
                    parts[1] = current_time
                elif action == 'leave':
                    last_join = datetime.strptime(parts[1], '%Y-%m-%d %H:%M:%S')
                    session_duration = datetime.now() - last_join
                    total_time = timedelta(seconds=int(parts[2])) + session_duration
                    parts[2] = str(total_time.total_seconds())
                f.write(','.join(parts) + '\n')
                player_found = True
            else:
                f.write(line)
        if not player_found and action == 'join':
            f.write(f"{player_name},{current_time},0\n")
        f.truncate()

def log_connection(server_name, action, address):
    log_file = datetime.now().strftime('%Y-%m-%d') + "_summary.log"
    current_time = datetime.now().strftime('%H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"{current_time} - {server_name} - {action} from {address}\n")

def generate_daily_summary():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    log_file = f"{yesterday}_summary.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
        os.rename(log_file, f"{yesterday}_summary.txt")
