# draw.io-nautobot-work

There is a demo here, sadly it's a little out of date:
https://youtu.be/ZwiIgBtmoMU


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



This will give you all the files you need, and give instructions on what to do.
`project = BuildNautobotProject(project_name)`
`project.full_build_project_with_help()`



