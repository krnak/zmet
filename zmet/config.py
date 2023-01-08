import yaml
import sys

self = sys.modules[__name__]

with open("config.yaml", 'r') as stream:
    try:
        _data = yaml.safe_load(stream)
        for k, v in _data.items():
            setattr(self, k, v)
        del _data
    except yaml.YAMLError as exc:
        print(exc)