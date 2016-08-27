from random import shuffle, choice
from os import path

dirPath = path.dirname(path.abspath(__file__))
USER_AGENT_FILE = path.join(dirPath.replace('source', '', 1), 'conf/userAgents.txt')

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
				uas.append(agent.strip()[1:-1])		# Remove quotes
		
	shuffle(uas)
	return choice(uas)

print LoadUserAgent()