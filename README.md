# draw.io-nautobot-work

There is a demo here, sadly it's a little out of date:
https://youtu.be/ZwiIgBtmoMU

The goal is to making building a Nautobot plugin much easier.  The idea is you bulid the database in draw.io, then use that file to build out the plugin.

the project name should be the same as the file name, but without the drawio part.   So for the file `test.drawio` file the project name would be `test`

Run `python3 build_db_with_class.py`to build the info about the drawio file, it will prompt you for the name of the project (the name of the file minus the .drawio part)

There are 2 ways to build the project:

- This will build out the basics of the plugin
  - `project=BuildNautobotProject(project_name)`
  - `project.build_project()`
  - This will build out:
    - `[name of the project]_plugin_files`
      - `plugin`
       - `[name of the project]`
            - `admin.py`
            - `filters.py`
            - `jobs.py`
            - `models.py`
            - `api`
                - `__init__.py`
                - `serilizers.py`
                - `urls.py`
                - `views.py`
- This way will build out everything `build_project()` does, **plus give instructions on how to install it**, and build out some other needed files.  
  - `project=BuildNautobotProject(project_name)`
  - `project.full_build_project_with_help()`
  - In addition to everything that build_projects build this will also build:
    - `[name of the project]_plugin_files` 
      - `plugin`    
        - `setup.py`
        - `[name of the project]`
            - `__init__.py`







