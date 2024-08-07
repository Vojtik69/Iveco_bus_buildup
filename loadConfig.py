import yaml
import os
import sys
# Get path to currently running script
currentDir = os.path.dirname(os.path.realpath(__file__))
# Add path to sys.path
sys.path.append(currentDir)

# load config file
with open(f'{currentDir}\config.yaml', 'r') as file:
    config = yaml.safe_load(file)
config['paths']['tcl'] = (currentDir + r'\tcl_functions.tcl').replace("\\", "/")
paths = config['paths']
