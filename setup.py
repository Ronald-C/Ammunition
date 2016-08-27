"""

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

try:
	with open(path.join(here, 'README.md'), 'rb') as readFile:
		long_description = f.read()

except Exception:
	long_description = ''

setup(
	name='roomGrab',
	version='2.0.0',
	description=long_description,
	url='',
	
	author='Ronald',
	author_email='',

	license='MIT',

	packages=find_packages(exclude=['roomGrab.test']),
	install_requires=['requests', 'beautifulsoup4'],

	entry_points={
		'console_scripts': [
			'attack=roomGrab:main'
		]
	}
)