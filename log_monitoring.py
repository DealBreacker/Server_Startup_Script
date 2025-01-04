import re, time
from iNotify_Simple import INotify, flags
from server_configs import monitoring, players_online, last_activity


def process_log_line(server_name, line, player_join_pattern, player_leave_pattern):
    join_match = player_join_pattern.search(line)
    leave_match = player_leave_pattern.search(line)
    if join_match:
        player = join_match.group(1)
        players_online[server_name].add(player)
    elif leave_match:
        player = leave_match.group(1)
        players_online[server_name].remove(player)
        if not players_online[server_name]:
            last_activity[server_name] = time.time()

def follow_log(server_name, log_file):
    inotify = INotify
    watch_flags = flags.modify | flags.CREATE
    inotify.add_watch(log_file, watch_flags)
    last_position = {server_name:0}
    player_join_pattern = re.compile(r' \[.*\] : (\w+) joined the game')
    player_leave_pattern = re.compile(r' \[.*\] : (\w+) left the game')
    with open(log_file, 'r') as f:
        last_position[server_name] = f.tell()
    while monitoring[server_name]:
        with open(log_file, 'r') as f:
            f.seek(last_position[server_name])
            for line in f:
                process_log_line(server_name, line, player_join_pattern, player_leave_pattern)
            last_position[server_name] = f.tell()
        time.sleep(0.5)
