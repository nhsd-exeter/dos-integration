#!/usr/bin/env python3

# TODO: Refactor

import os
import sys
import yaml

fin = str(sys.argv[1])
fout = str(sys.argv[2])
build_id = str(os.environ["BUILD_ID"])
yml = {}

with open(fin) as file:
    yml = yaml.load(file, Loader=yaml.FullLoader)
    for service in list(yml["services"].keys()):
        yml["services"][service]["container_name"] = yml["services"][service]["container_name"] + "-" + str(build_id)
        if "depends_on" in yml["services"][service]:
            items = []
            for depends_on in list(yml["services"][service]["depends_on"]):
                items.append(depends_on + "-" + str(build_id))
            yml["services"][service]["depends_on"] = items
        yml["services"][service + "-" + str(build_id)] = yml["services"].pop(service)

with open(fout, "w") as file:
    yaml.dump(yml, file, default_flow_style=False)
