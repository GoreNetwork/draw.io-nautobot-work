from constants import *
import os


def to_doc_w(file_name, varable):
    f = open(file_name, "w")
    f.write(varable)
    f.close()


if os.environ.get("project_name") == None:
    project_name = input(
        "The name of the draw.io file should be the name of the plugin.  Please enter the name of the plugin (Example: dnd_builder.drawio would be dnd_builder): "
    )
    os.environ["project_name"] = project_name
if os.environ.get("plugin_description") == None:
    plugin_description = input("Plugin description: ")
    os.environ["plugin_description"] = plugin_description
if os.environ.get("plugin_author") == None:
    plugin_author = input("Author of the plugin: ")
    os.environ["plugin_author"] = plugin_author
project_name = os.environ.get("project_name")

setup_file_content = setup_file.render(
    project_name=os.environ.get("project_name"),
    plugin_description=os.environ.get("plugin_description"),
    plugin_author=os.environ.get("plugin_author"),
)

os.system("python3 build_db.py")
file_name = f"./{project_name}_files/plugin/setup.py"
to_doc_w(file_name, setup_file_content)


init_file_content = init_file.render(
    project_name=os.environ.get("project_name"),
    plugin_description=os.environ.get("plugin_description"),
    plugin_author=os.environ.get("plugin_author"),
)

file_name = f"./{project_name}_files/plugin/{project_name}/__init__.py"
to_doc_w(file_name, init_file_content)


default_location = "/opt/naubot/"
instructions = [
    f"""This assumes you have done the tasks on https://nautobot.readthedocs.io/en/stable/installation/ and https://nautobot.readthedocs.io/en/stable/installation/nautobot/
If you know Ansible this will setup most of the Nautobot for you: https://github.com/GoreNetwork/install-nautobot however it's not being kept up
"""
    f"""On occastion there may be issues with permissions, by default 
chmod -R 777 {default_location} 
will fix it, but never do this on a device where security matters even a little bit!""",
    f"""copy the plugin folder under {project_name}_files to naubot home (Default: {default_location}) """,
    f"""edit nautobot_config.py by putting the string {project_name} inside the PLUGINS list
It should look like this:
PLUGINS = ['{project_name}']
                """,
    f"""inside the plugin folder on the naubtobot server as the naubot user (sudo -iu nautobot) run:
                 "python setup.py develop" """,
    f'''Next we need to make the migrations as part of the building out the database with:
                "nautobot-server makemigrations {project_name}"''',
    f'''Next we need to apply said migrations with:
                "nautobot-server migrate {project_name}"''',
    f'Run the demo server with "nautobot-server runserver 0.0.0.0:8081 --insecure"',
]

for each in instructions:
    print("\n")
    print(each)
    input("Press return for next step: ")
