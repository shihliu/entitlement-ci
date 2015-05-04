"""
    Quick script to extract resources and populate
    RESOURCES.txt
"""

import json
import os

RESOURCES_INPUT = os.environ.get('RESOURCES_INPUT', 'resources.json')
RESOURCES_OUTPUT = os.environ.get('RESOURCES_OUTPUT', 'RESOURCES.txt')

input_file = open(RESOURCES_INPUT, 'r')
data = json.load(input_file)
input_file.close


f = open(RESOURCES_OUTPUT, 'w')
for idx, resources in data.iteritems():
    for resource in resources:
        if 'nodes' in resource:
            for idx, nodes in resource.iteritems():
                for node in nodes:
                    if 'ip' in node:
                        f.write(node['ip'] + ",")
f.write("\n")
f.close()
