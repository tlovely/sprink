import json
import os

with open('.config.default.json') as out:
	_config = json.load(out)

if os.path.exists('.config.json'):
	with open('.config.json') as out:
		_config = {
			**_config,
			**json.load(out)
		}

_globals = globals()

for key, value in _config.items():
	_globals[key] = value

__all__ = list(_config) 