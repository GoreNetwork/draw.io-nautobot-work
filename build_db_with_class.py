from DrawIoNautobot import BuildNautobotProject
from pprint import pprint
import os

def countlines(start, lines=0, header=True, begin_start=None):
    if header:
        print("{:>10} |{:>10} | {:<20}".format("ADDED", "TOTAL", "FILE"))
        print("{:->11}|{:->11}|{:->20}".format("", "", ""))

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith(".py"):
                with open(thing, "r") as f:
                    newlines = f.readlines()
                    newlines = len(newlines)
                    lines += newlines

                    if begin_start is not None:
                        reldir_of_thing = "." + thing.replace(begin_start, "")
                    else:
                        reldir_of_thing = "." + thing.replace(start, "")

                    print(
                        "{:>10} |{:>10} | {:<20}".format(
                            newlines, lines, reldir_of_thing
                        )
                    )

if os.environ.get("project_name") == None:
    project_name = input(
        "The name of the draw.io file should be the name of the plugin.  Please enter the name of the plugin (Example: dnd_builder.drawio would be dnd_builder): "
    )
    os.environ["project_name"] = project_name
project_name = os.environ.get("project_name")

project = BuildNautobotProject(project_name)

# pprint(project.table_data)
# project.build_project()
project.full_build_project_with_help()
# print (f"./{project.project_name}_files")
# lines_saved = countlines(start=f"./{project.project_name}_files")