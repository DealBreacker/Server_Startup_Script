# logging_system.py
import os
import json
from datetime import datetime, timedelta

def create_log_directories():
    os.makedirs("summary_logs", exist_ok=True)
    os.makedirs("server_logs", exist_ok=True)

def rollover_server_logs(server_name):
    current_date = datetime.now().strftime('%Y-%m-%d')
    new_log_file = os.path.join("server_logs", f"{server_name}_{current_date}.log")
    if not os.path.exists(new_log_file):
        with open(new_log_file, 'w') as f:
            f.write(f"Log file for {server_name} - {current_date}\n")
    return new_log_file

def rollover_summary_logs():
    current_date = datetime.now().strftime('%Y-%m-%d')
    summary_log_file = os.path.join("summary_logs", f"{current_date}_summary.log")
    if not os.path.exists(summary_log_file):
        with open(summary_log_file, 'w') as f:
            f.write(f"Summary log for {current_date}\n")
    return summary_log_file

def initialize_log_files(server_names):
    create_log_directories()
    for server_name in server_names:
        rollover_server_logs(server_name)
    rollover_summary_logs()

def log_connection(server_name, action, address):
    log_file = rollover_server_logs(server_name)
    current_time = datetime.now().strftime('%H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"{current_time} - {action} from {address}\n")

def update_player_log(server_name, player_name, action, duration=None):
    log_file = rollover_server_logs(server_name)
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
                    total_time = timedelta(seconds=float(parts[2])) + session_duration
                    parts[2] = str(total_time.total_seconds())
                f.write(','.join(parts) + '\n')
                player_found = True
            else:
                f.write(line)
        if not player_found and action == 'join':
            f.write(f"{player_name},{current_time},0\n")
        f.truncate()

def generate_daily_summary():
    summary_log = rollover_summary_logs()
    # Your existing code for generating daily summary
    # Write the summary to the summary_log file
    pass

def save_state(players_online, last_activity):
    state = {
        'players_online': {k: list(v) for k, v in players_online.items()},
        'last_activity': last_activity
    }
    with open('server_state.json', 'w') as f:
        json.dump(state, f)

def load_state():
    try:
        with open('server_state.json', 'r') as f:
            state = json.load(f)
        players_online = {k: set(v) for k, v in state['players_online'].items()}
        last_activity = state['last_activity']
        return players_online, last_activity
    except FileNotFoundError:
        return None, None
