import zlib
import base64
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from pprint import pprint
import xmltodict
import json
import yaml
import os
from constants import *
# import argparse

# parser = argparse.ArgumentParser(description='Builds out files for natubot from draw.io')
# parser.add_argument("--plugin_name", help="the name used for the classes, example: SwitchHelper")
# args = parser.parse_args()
# pprint (dir(args.plugin_name))
# plugin_name = args.plugin_name



# filename = "DB design (4).drawio"
filename = "scrap_work.drawio"
filename = 'nautobot_robot_platform_data.drawio'
project_name = filename.split('.')[0]

def normalize_column_name(column):
    if "***ForeignKey" in column:
        source_table = pull_source_table_for_fk(column)
        column= f"{source_table}_FK"
    if column == "PK" or column[-3:]=="_PK":
        return None
    column = column.replace(' ','_')
    return column

def normalise_table_name(table_name):
    table_name=table_name.replace(' ','_')
    return table_name

def readed_in_draw_io_file(filename):

    tree = ET.parse(filename)
    data = base64.b64decode(tree.find('diagram').text)
    xml = zlib.decompress(data, wbits=-15)
    xml =xml.decode("utf-8")
    xml = unquote(xml)
    my_dict = xmltodict.parse(xml, dict_constructor=dict)
    return my_dict



def build_flatened_data(db_data_raw):
    output = {}
    output['arrows'] = {}
    for cell in db_data_raw['mxGraphModel']['root']['mxCell']:
        if '@value' in cell:
            output[cell['@id']]={}
            output[cell['@id']]['value']=cell['@value']
            output[cell['@id']]['parent']=cell['@parent']
        if '@edge' in cell:
            output['arrows'][cell['@id']]={}
            output['arrows'][cell['@id']]={}
            output['arrows'][cell['@id']]['source']=cell['@source']
            output['arrows'][cell['@id']]['target']=cell['@target']


    write_yml_file(output, 'flat_DB_data.yml')

    return output

def write_yml_file(dictionary, output_file_name):
    with open(output_file_name, 'w') as outfile:
        yaml.dump(dictionary, outfile)

def find_table_value_from_column_value(input, key):
    parent_id = input[key]['parent']
    return input[parent_id]['value']




def build_table_data(input):
    tables = {}
    columns = []
    for each in input:
        if each=="arrows":
            continue
        if input[each]['parent']=='1':
            tables[each]={}
            tables[each]['name']=input[each]['value']
            tables[each]['column']=[]
        else:
            columns.append(input[each])
    for each in columns:
        tables[each['parent']]['column'].append(each['value'])
    output =[]
    for each in tables:
        output.append(tables[each])

    for each in input['arrows']:
        relationship={}
        relationship['relationship']={}
        source_cell_id = input['arrows'][each]['source']
        target_cell_id = input['arrows'][each]['target']
        source=find_table_value_from_column_value(input,source_cell_id)
        target=find_table_value_from_column_value(input,target_cell_id)
        for each in output:
            if each['name'] == target:
                each['column'].append(f"***ForeignKey:{source}***")



    
    return output

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

def pull_source_table_for_fk(column):
    column=column.replace("*","")
    column=column.replace("ForeignKey:","")
    column=column.replace(' ','_')
    return column

def build_models(table_data):
#     model_data = '''"""Model definition for robot_platform_data."""
# from django.db import models
# from nautobot.core.models import BaseModel
# from nautobot.core.models.generics import OrganizationalModel, PrimaryModel
# from datetime import datetime

# model_type=PUT YOUR MODEL TYPE HERE!!
# '''
    model_data = model_table_imports.render()
    for each in table_data:
        if 'relationship' in each:
            continue
        table_name = normalise_table_name(each['name'])
        model_data=model_data+model_class_head_template.render(table_name=table_name)
        for column in each['column']:
            if "***ForeignKey" not in column:
                column=normalize_column_name(column)
                if column==None:
                    continue
                column=column.replace(' ','_')
                model_data=model_data+model_class_body_non_foreign_key.render(column=column)
            else:
                source_table = pull_source_table_for_fk(column)
                key_name= f"{source_table}_FK"
                model_data=model_data+model_class_body_foreign_key.render(source_table=source_table, key_name=key_name)
                
    filename= project_name+"/models.py"
    to_doc_w(filename, model_data)

def build__init__(api_path):
    file_name = f"{api_path}/__init__.py"
    to_doc_w(file_name, '')

def build_serializers(table_data, api_path):
    table_names = []
    for table in table_data:
        table_name = normalise_table_name(table['name'])
        table_names.append(table_name)
    output = seralizer_imports.render(project_name=project_name, table_names=table_names)
    for table in table_data:
        columns = []
        table_name = normalise_table_name(table['name'])

        for column in table['column']:
            column = normalize_column_name(column)
            if column==None:
                continue
            column = column.replace(' ','_')
            columns.append(column)
        output = output+serlizer_classes.render(table_name=table_name, columns=columns)
    filename = f"{api_path}/serializers.py"
    to_doc_w(filename, output)
    

def build_filters(table_name):
    output = """from nautobot.utilities.filters import BaseFilterSet
import django_filters
from django.utils import timezone
from .models import  """
    for table in table_data:
        table_name = normalise_table_name(table['name'])
        output = output+f"{table_name}, "
    output = output[:-2]
    for table in table_data:
        table_name = normalise_table_name(table['name'])
        output = output+f"""

class {table_name}FilterSet(django_filters.FilterSet):
    class Meta:
        model = {table_name}
        fields = ("""
        for column in table['column']:
            column = normalize_column_name(column)
            if column==None:
                continue
            column = column.replace(' ','_')
            output = output + f'"{column}", '


        output = f"""{output})"""
    filename = f"{project_name}/filters.py"
    to_doc_w(filename, output)
    

def build_api_views(table_data, api_path):
    models = ''
    serializers=''
    filter_sets=''
    num = 0
    for each_table in table_data:
        table_name = normalise_table_name(each_table['name'])
        if num==0:
            models = f"{models} {table_name}"
            serializers=f"{serializers} {table_name}Serializer"
            filter_sets=f"{filter_sets} {table_name}FilterSet"
        else:
            models = f"{models}, {table_name}"
            serializers=f"{serializers}, {table_name}Serializer"
            filter_sets=f"{filter_sets}, {table_name}FilterSet"
        num = num+1
        output = f"""from nautobot.core.api.views import ModelViewSet
from {project_name}.models import {models}
from .serializers import {serializers}
from {project_name}.filters import {filter_sets}
"""
    for each_table in table_data:
        table_name = normalise_table_name(each_table['name'])
        output=f"""{output}
    
class {table_name}ViewSet(ModelViewSet):
    queryset = {table_name}.objects.all()
    filterset_class = {table_name}FilterSet
    serializer_class = {table_name}Serializer
    """
    filename = f"{api_path}/views.py"
    to_doc_w(filename, output)    


def build_api_urls(table_data, api_path):
    output = f"""from nautobot.core.api.routers import OrderedDefaultRouter
from {project_name}.api import views

router = OrderedDefaultRouter()

"""
    for each_table in table_data:
        table_name = normalise_table_name(each_table['name'])
        output=f"""{output}router.register("{table_name}", views.{table_name}ViewSet)
"""
    output = f"{output}urlpatterns = router.urls"
    filename = f"{api_path}/urls.py"
    to_doc_w(filename, output)    


def build_api_data(table_data):
    api_path = f"./{project_name}"
    if os.path.exists(api_path)==False:
        os.makedirs(api_path)
    api_path = f"{project_name}/api"
    if os.path.exists(api_path)==False:
        os.makedirs(api_path)
    build__init__(api_path)
    build_serializers(table_data, api_path)
    build_filters(table_data)
    build_api_views(table_data, api_path)
    build_api_urls(table_data, api_path)

database_data_raw=readed_in_draw_io_file(filename)
flat_data = build_flatened_data(database_data_raw)
table_data = build_table_data(flat_data)     
build_api_data(table_data)   
build_models(table_data,)

def build_admin(table_data):
    table_name_list = []
    for table in table_data:
        table_name_list.append(table['name'])
    output=admin_table_imports.render(table_name_list=table_name_list, project_name=project_name)
    for table in table_data:
        table_name = table['name']
        columns = []
        for column in table['column']:
            column = normalize_column_name(column)
            if column==None:
                continue
            columns.append(column)
        admin_class = admin_class_template.render(table_name =table_name, columns=columns)
        output = f"{output} {admin_class}"
    filename= f"{project_name}/admin.py"
    to_doc_w(filename, output) 

build_admin(table_data)


