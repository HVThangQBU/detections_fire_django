import yaml
path = 'detections/config.yml'
with open(path) as f:
  config = yaml.load(f, Loader=yaml.FullLoader)
args = config
