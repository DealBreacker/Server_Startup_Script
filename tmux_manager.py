# tmux_killer.py
import subprocess

def kill_tmux_sessions():
    result = subprocess.run(['tmux', 'list-sessions', '-F', '#{session_name}'], capture_output=True, text=True)
    session_names = result.stdout.strip().split('\n')
    for session_name in session_names:
        subprocess.run(['tmux', 'kill-session', '-t', session_name])
    print("All tmux sessions killed.")
