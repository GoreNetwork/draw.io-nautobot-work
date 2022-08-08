# draw.io-nautobot-work

There is a demo here, sadly it's a little out of date:
https://youtu.be/ZwiIgBtmoMU


Run 
python3 build_db_with_class.py 
to build the info about the drawio file, it will prompt you for the name of the project (the name of the file minus the .drawio part)

There are 2 ways to run:
This will build out the basics of the plugin
`project=BuildNautobotProject(project_name)`
`project.build_project()`

This will give you all the files you need, and give instructions on what to do.
`project = BuildNautobotProject(project_name)`
`project.full_build_project_with_help()`



