import re
import time
from inotify_simple import INotify, flags
from server_configs import monitoring, players_online, last_activity
from logging_system import update_player_log

def process_log_line(server_name, line, player_join_pattern, player_leave_pattern):
    join_match = player_join_pattern.search(line)
    leave_match = player_leave_pattern.search(line)
    if join_match:
        player = join_match.group(1)
        players_online[server_name].add(player)
        update_player_log(server_name, player, 'join')
    elif leave_match:
        player = leave_match.group(1)
        if player in players_online[server_name]:
            players_online[server_name].remove(player)
            update_player_log(server_name, player, 'leave')
        if not players_online[server_name]:
            last_activity[server_name] = time.time()

def follow_log(server_name, log_file):
    inotify = INotify()
    watch_flags = flags.MODIFY | flags.CREATE
    wd = inotify.add_watch(log_file, watch_flags)
    last_position = 0
    player_join_pattern = re.compile(r' \[.*\] : (\w+) joined the game')
    player_leave_pattern = re.compile(r' \[.*\] : (\w+) left the game')
    
    with open(log_file, 'r') as f:
        f.seek(0, 2)  # Move to the end of the file
        last_position = f.tell()
    
    while monitoring[server_name]:
        for event in inotify.read(timeout=1000):
            if event.mask & flags.MODIFY:
                with open(log_file, 'r') as f:
                    f.seek(last_position)
                    for line in f:
                        process_log_line(server_name, line, player_join_pattern, player_leave_pattern)
                    last_position = f.tell()
        time.sleep(0.1)
    
    inotify.rm_watch(wd)
