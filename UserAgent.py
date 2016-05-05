from random import shuffle, choice
from os import path

dirPath = path.dirname(path.abspath(__file__))
USER_AGENT_FILE = path.join(dirPath, 'user_agents.txt')

def LoadUserAgent(ua_file=USER_AGENT_FILE):
	"""
	:ua_file : string
		Path to text file of user agents; one per line
	"""
	assert isinstance(ua_file, str)

	uas = []
	with open(ua_file, 'rb') as uaf:
		for agent in uaf:
			if agent:
				uas.append(agent.strip()[1:-1-1])

	shuffle(uas)	# Shuffle user agents list
	return choice(uas)	# Return a randomly choosen user agent
