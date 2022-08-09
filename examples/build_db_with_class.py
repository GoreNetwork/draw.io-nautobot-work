from nautobot_plugin_builder import BuildNautobotProject
from pprint import pprint
import os

if os.environ.get("project_name") == None:
    project_name = input(
        "The name of the draw.io file should be the name of the plugin.  Please enter the name of the plugin (Example: dnd_builder.drawio would be dnd_builder): "
    )
    os.environ["project_name"] = project_name
project_name = os.environ.get("project_name")

project = BuildNautobotProject(project_name)

# Builds with helpful steps
project.full_build_project_with_help()

# Builds out the core of the plugin, but not setup.py, or __init__.py
# project.build_project()
