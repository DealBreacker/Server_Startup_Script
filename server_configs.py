# Configuration for multiple servers
import time
SERVER_CONFIGS = {
    'dalylas_server': {
        'host': '192.168.1.130',
        'port': 25566,
        'startup_script': '/home/dealbreacker/servers/dalyla_1.20.6_server/',
        'startup_program': './start.sh',
	'log_file': '/home/dealbreacker/servers/dalyla_1.20.6_server/logs/latest.log'
    },
    'bros_server': {
        'host': '192.168.1.130',
        'port': 25567,
        'startup_script': '/home/dealbreacker/servers/bros_server_1.21.2/',
        'startup_program': './start.sh',
	'log_file': '/home/dealbreacker/servers/bros_server_1.21.2/logs/latest.log'
    },
    'all_of_fabric': {
        'host': '192.168.1.130',
        'port': 25568,
        'startup_script': '/home/dealbreacker/servers/all_of_fabric_7_2.3.0/',
        'startup_program': './startserver.sh',
	'log_file': '/home/dealbreacker/servers/all_of_fabric_7_2.3.0/logs/latest.log'
    },
    'all_the_mods_9-THS': {
        'host': '192.168.1.130',
	'port': 25570,
	'startup_script': '/home/dealbreacker/servers/all_the_mods_9-TO_THE_SKY/',
	'startup_program': './startserver.sh',
	'log_file': '/home/dealbreacker/servers/all_the_mods_9-TO_THE_SKY/logs/latest.log'
    }
}
#~~~~~~~~~~~~~~ This is the location for servers that are currently under maintinance/out of comission~~~~~~~~~
#    'Creative_Server': {
#        'host': '192.168.1.130',
#        'port': 25569,
#        'startup_script': '/home/dealbreacker/servers/creative_server/',
#        'startup_program': './start.sh',
#	'log_file': '/home/dealbreacker/servers/creative_server/logs/latest.log'

    # Add more servers as needed

# Dictionary to track last activity time for servers:
last_activity = {server_name: time.time() for server_name in SERVER_CONFIGS}
players_online = {server_name: set() for server_name in SERVER_CONFIGS}
monitoring = {server_name: False for server_name in SERVER_CONFIGS}