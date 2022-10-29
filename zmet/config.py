import yaml
import sys

with open("config.yaml", 'r') as stream:
    try:
        _data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

self = sys.modules[__name__]
for k, v in _data.items():
    setattr(self, k, v)

del _data
