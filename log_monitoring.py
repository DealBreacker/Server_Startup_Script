import re
import time, os
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
        print(f"{player} joined {server_name}")
    elif leave_match:
        player = leave_match.group(1)
        if player in players_online[server_name]:
            players_online[server_name].remove(player)
            update_player_log(server_name, player, 'leave')
            print(f"{player} left {server_name}")
        if not players_online[server_name]:
            last_activity[server_name] = time.time()
            print(f"Last activity time for {server_name} is {last_activity[server_name]}")

def follow_log(server_name, log_file):
    print(f"Starting log monitoring for {server_name}\n")

    inotify = INotify()
    watch_flags = flags.MODIFY | flags.CREATE
    wd = inotify.add_watch(log_file, watch_flags)
    monitoring[server_name] = True

    player_join_pattern = re.compile(r'\[.*\]: (\w+) joined the game')
    player_leave_pattern = re.compile(r'\[.*\]: (\w+) left the game')

    # Initial read of existing content
    with open(log_file, 'r') as f:
        for line in f:
            process_log_line(server_name, line, player_join_pattern, player_leave_pattern)
    
    last_position = os.path.getsize(log_file)

    while monitoring[server_name]:
        for event in inotify.read(timeout=1000):
            if event.mask & flags.MODIFY:
                with open(log_file, 'r') as f:
                    f.seek(last_position)
                    for line in f:
                        process_log_line(server_name, line, player_join_pattern, player_leave_pattern)
                    last_position = f.tell()

    inotify.rm_watch(wd)
    print(f"Stopping log monitoring for {server_name}\n")

