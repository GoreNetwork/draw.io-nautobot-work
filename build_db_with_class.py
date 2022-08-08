from DrawIoNautobot import BuildNautobotProject
from pprint import pprint
import os


if os.environ.get("project_name") == None:
    project_name = input(
        "The name of the draw.io file should be the name of the plugin.  Please enter the name of the plugin (Example: dnd_builder.drawio would be dnd_builder): "
    )
    os.environ["project_name"] = project_name
project_name = os.environ.get("project_name")

project = BuildNautobotProject(project_name)

pprint (project.table_data)
# project.build_project()
project.full_build_project_with_help()