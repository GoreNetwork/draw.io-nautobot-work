from . import constants
import zlib
import base64
import xml.etree.ElementTree as ET
import xmltodict
from urllib.parse import unquote
import yaml
from pprint import pprint
import os

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

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isdir(thing):
            lines = countlines(thing, lines, header=False, begin_start=start)

    return lines

def write_yml_file(dictionary, output_file_name):
    with open(output_file_name, "w") as outfile:
        yaml.dump(dictionary, outfile)

def to_doc_w(file_name, varable):
    f = open(file_name, "w")
    f.write(varable)
    f.close()

class ReadInDrawIoNautobot:
    def __init__(self, project_name):
        self.project_name = project_name
        self.db_data_raw = self.readed_in_draw_io_file()
        self.flat_data = self.build_flatened_data()
        self.table_data = self.build_table_data()
        self.tables = self.find_tables()
        

    def find_tables(self):
        table_data = self.table_data
        tables = []
        for table in table_data:
            tables.append(table["name"])
        return tables

    def pull_source_table_for_fk(self, column):
        column = column.replace("*", "")
        column = column.replace("ForeignKey:", "")
        column = column.replace(" ", "_")
        return column

    def normalize_columns_names(self, columns):
        normalized_columns = []
        for column in columns:
            column = self.normalize_column_name(column)
            if column == None:
                continue
            column = column.replace(" ", "_")
            normalized_columns.append(column)
        return normalized_columns

    def normalize_column_name(self, column):
        if "***ForeignKey" in column:
            source_table = self.pull_source_table_for_fk(column)
            column = f"{source_table}_FK"
        if column == "PK" or column[-3:] == "_PK":
            return None
        column = column.replace(" ", "")
        if "," in column:
            column = column.split(",")
            column = column[0]
        return column

    def readed_in_draw_io_file(self):
        filename = f"{self.project_name}.drawio"
        tree = ET.parse(filename)
        data = base64.b64decode(tree.find("diagram").text)
        xml = zlib.decompress(data, wbits=-15)
        xml = xml.decode("utf-8")
        xml = unquote(xml)
        my_dict = xmltodict.parse(xml, dict_constructor=dict)
        return my_dict

    def build_flatened_data(self):
        db_data_raw = self.db_data_raw
        output = {}
        output["arrows"] = {}
        for cell in db_data_raw["mxGraphModel"]["root"]["mxCell"]:
            if "@value" in cell:
                output[cell["@id"]] = {}
                output[cell["@id"]]["value"] = cell["@value"]
                output[cell["@id"]]["parent"] = cell["@parent"]
            if "@edge" in cell:
                output["arrows"][cell["@id"]] = {}
                output["arrows"][cell["@id"]] = {}
                output["arrows"][cell["@id"]]["source"] = cell["@source"]
                output["arrows"][cell["@id"]]["target"] = cell["@target"]

        write_yml_file(output, "flat_DB_data.yml")

        return output

    def find_table_value_from_column_value(self, input, key):
        parent_id = input[key]["parent"]
        return input[parent_id]["value"]

    def build_table_data(self):
        input = self.flat_data
        tables = {}
        columns = []
        for each in input:
            if each == "arrows":
                continue
            if input[each]["parent"] == "1":
                tables[each] = {}
                tables[each]["name"] = input[each]["value"]
                tables[each]["column"] = []
            else:
                columns.append(input[each])
        for each in columns:
            tables[each["parent"]]["column"].append(each["value"])
        output = []
        for each in tables:
            output.append(tables[each])

        for each in input["arrows"]:
            relationship = {}
            relationship["relationship"] = {}
            source_cell_id = input["arrows"][each]["source"]
            target_cell_id = input["arrows"][each]["target"]
            source = self.find_table_value_from_column_value(input, source_cell_id)
            target = self.find_table_value_from_column_value(input, target_cell_id)
            for each in output:
                if each["name"] == target:
                    each["column"].append(f"***ForeignKey:{source}***")

        for table in output:
            table["normalized_columns"] = self.normalize_columns_names(table["column"])
            table['normalized_table_name']=self.normalise_table_name(table['name'])

        return output


class BuildNautobotProject(ReadInDrawIoNautobot):
    def build_project_dict_structure(self):
        project_name = self.project_name
        tmp_paths = [
            f"./{project_name}_files",
            f"./{project_name}_files/plugin",
            f"./{project_name}_files/plugin/{project_name}",
            f"./{project_name}_files/plugin/{project_name}/api",
        ]
        for path in tmp_paths:
            if os.path.exists(path) == False:
                os.makedirs(path)
        self.api_path = f"./{project_name}_files/plugin/{project_name}/api"

    def normalize_column_name_for_models(self, column):
        if "***ForeignKey" in column:
            source_table = self.pull_source_table_for_fk(column)
            column = f"{source_table}_FK"
        if column == "PK" or column[-3:] == "_PK":
            return None
        column = column.replace(" ", "")

        if "," in column:
            column = column.split(",")
        return column

    def normalise_table_name(self, table_name):
        table_name = table_name.replace(" ", "_")
        return table_name

    def find_feild_types(self, table_data):
        # pprint (table_data)
        feild_types_in_tables = []
        for each in table_data:
            if "relationship" in each:
                continue
            for column in each["column"]:
                if ',' in column:
                    column=column.split(',')
                if type(column) == list:
                    key_name, feild_type = column[0], column[1]
                    feild_types_in_tables.append(feild_type)
        return feild_types_in_tables

    def build_models(self):
        project_name = self.project_name
        table_data = self.table_data
        defaults_for_fields = {
            # "name of feild type": {"default_value_name":"thing that needs a default value",
            #                    "default_value": "What the default value should be" },
            "CharField": {"default_value_name": "max_length", "default_value": "100"},
            "DateField": {"default_value_name": "auto_now", "default_value": "False"},
            "FilePathField": {"default_value_name": "path", "default_value": "Ted"},
        }

        feild_types_in_tables = self.find_feild_types(table_data)
        print(feild_types_in_tables)

        model_data = constants.model_table_imports.render(
            feild_types_in_tables=feild_types_in_tables,
            defaults_for_fields=defaults_for_fields,
        )

        for each in table_data:
            if "relationship" in each:
                continue
            table_name = each['normalized_table_name']
            model_data = model_data + constants.model_class_head_template.render(
                table_name=table_name
            )
            for column in each["column"]:
                if "," in column:
                    column = column.split(',')
                feild_type = "TextField"
                if "***ForeignKey" not in column:
                    if " " in column:
                        column = self.normalize_column_name_for_models(column)
                        print(column)
                    if type(column) == list:
                        key_name, feild_type = column[0], column[1]
                        feild_type = feild_type.replace(" ", "")
                    elif column == None:
                        continue
                    else:
                        key_name = column
                    model_data = model_data + constants.model_class_body_non_foreign_key.render(
                        column=key_name,
                        feild_type=feild_type,
                        defaults_for_fields=defaults_for_fields,
                    )
                else:
                    source_table = self.pull_source_table_for_fk(column)
                    key_name = f"{source_table}_FK"
                    model_data = model_data + constants.model_class_body_foreign_key.render(
                        project_name=project_name,
                        source_table=source_table,
                        key_name=key_name,
                    )

        filename = f"./{project_name}_files/plugin/{project_name}/models.py"
        to_doc_w(filename, model_data)

    def build__init__(self):
        file_name = f"./{self.api_path }/__init__.py"
        to_doc_w(file_name, "")

    def build_serializers(self):
        table_data = self.table_data
        table_names = []
        for table in table_data:
            table_name = table["normalized_table_name"]
            table_names.append(table_name)
        output = constants.seralizer_imports.render(
            project_name=project_name, table_names=table_names
        )
        for table in table_data:
            columns = table["normalized_columns"]
            table_name = table['normalized_table_name']
            output = output + constants.serlizer_classes.render(
                table_name=table_name, columns=columns
            )
        filename = f"./{self.api_path}/serializers.py"
        to_doc_w(filename, output)

    def build_serializers(self):
        table_data = self.table_data
        table_names = []
        for table in table_data:
            table_names.append(table['normalized_table_name'])
        output = constants.seralizer_imports.render(
            project_name=self.project_name, table_names=table_names
        )
        for table in table_data:
            columns = table["normalized_columns"]
            table_name = table['normalized_table_name']

            output = output + constants.serlizer_classes.render(
                table_name=table_name, columns=columns
            )
        filename = f"./{self.api_path}/serializers.py"
        to_doc_w(filename, output)

    def build_filters(self):
        table_data = self.table_data
        tables = self.tables
        project_name = self.project_name
        output = constants.filter_imports.render(tables=tables)

        for table in table_data:
            columns = table["normalized_columns"]
            table_name = table['normalized_table_name']
            output = output + constants.filter_classes.render(
                table_name=table_name, columns=columns
            )
        filename = f"./{project_name}_files/plugin/{project_name}/filters.py"
        to_doc_w(filename, output)

    def build_api_views(self):
        tables = self.tables
        output = constants.api_views_imports.render(tables=tables, project_name=self.project_name)

        for table in tables:
            output = output + constants.api_classes_imports.render(table=table)

        filename = f"./{self.api_path }/views.py"
        to_doc_w(filename, output)

    def build_api_urls(self):
        output = constants.api_urls_imports.render(project_name=self.project_name)
        for each_table in self.table_data:
            table_name = each_table['normalized_table_name']
            output = output + constants.api_urls_classes.render(table_name=table_name)
        output = output + "urlpatterns = router.urls"
        filename = f"./{self.api_path }/urls.py"
        to_doc_w(filename, output)

    def build_admin(self):
        table_name_list = []
        for table in self.table_data:
            table_name_list.append(table["name"])
        output = constants.admin_table_imports.render(
            table_name_list=table_name_list, project_name=self.project_name
        )
        for table in self.table_data:
            table_name = table["name"]
            columns = table["normalized_columns"]
            admin_class = constants.admin_class_template.render(
                table_name=table_name, columns=columns
            )
            output = f"{output} {admin_class}"
        filename = f"./{self.project_name}_files/plugin/{self.project_name}/admin.py"
        to_doc_w(filename, output)

    def build_jobs_get_or_create(self):
        tables = []
        for table in self.table_data:
            tables.append(table["name"])
        output = constants.jobs_header.render(tables=tables, project_name=self.project_name)
        for table in self.table_data:
            table_name = table["name"]
            columns = table["normalized_columns"]
            log_message = ""
            for column in columns:
                log_message = log_message + "{" + column + "},"
            log_message = log_message[0:-1]
            output = output + constants.jobs_get_or_create.render(
                table_name=table_name, columns=columns, log_message=log_message
            )
        filename = f"./{self.project_name}_files/plugin/{self.project_name}/jobs.py"
        to_doc_w(filename, output)

    def build_project(self):
        self.build_project_dict_structure()
        self.build_models()
        self.build__init__()
        self.build_serializers()
        self.build_filters()
        self.build_api_views()
        self.build_api_urls()
        self.build_admin()
        self.build_jobs_get_or_create()

    def build_setup_files(self):
        project_name = self.project_name
        if os.environ.get("plugin_description") == None:
            plugin_description = input("Plugin description: ")
            os.environ["plugin_description"] = plugin_description
        if os.environ.get("plugin_author") == None:
            plugin_author = input("Author of the plugin: ")
            os.environ["plugin_author"] = plugin_author

        setup_file_content = constants.setup_file.render(
            project_name=self.project_name,
            plugin_description=os.environ.get("plugin_description"),
            plugin_author=os.environ.get("plugin_author"),
        )
        self.build_project()
        file_name = f"./{self.project_name}_files/plugin/setup.py"
        to_doc_w(file_name, setup_file_content)

        init_file_content = constants.init_file.render(
            project_name=os.environ.get("project_name"),
            plugin_description=os.environ.get("plugin_description"),
            plugin_author=os.environ.get("plugin_author"),
        )

        file_name = (
            f"./{self.project_name}_files/plugin/{self.project_name}/__init__.py"
        )
        to_doc_w(file_name, init_file_content)

    def full_build_project_with_help(self):
        project_name = self.project_name
        self.build_setup_files()
        default_location = "/opt/nautobot/"
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
        print("\n\n\n")
        lines_saved = countlines(start=f"./{project_name}_files")
        print(f"\n\nThis program saved you {lines_saved} lines of code")
