import zlib
import base64
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from pprint import pprint
import xmltodict
import json
import yaml
import os
# import argparse

# parser = argparse.ArgumentParser(description='Builds out files for natubot from draw.io')
# parser.add_argument("--plugin_name", help="the name used for the classes, example: SwitchHelper")
# args = parser.parse_args()
# pprint (dir(args.plugin_name))
# plugin_name = args.plugin_name



# filename = "DB design (4).drawio"
filename = "scrap_work.drawio"

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

def build_models(table_data):
    model_data = '''"""Model definition for robot_platform_data."""
from django.db import models
from nautobot.core.models import BaseModel, OrganizationalModel, PrimaryModel
from datetime import datetime

model_type=PUT YOUR MODEL TYPE HERE!!
'''
    for each in table_data:
        if 'relationship' in each:
            continue
        name = each['name'].replace(' ','_')
        model_data=model_data+ f"""
class {name}(model_type):
"""
        for column in each['column']:
            if "***ForeignKey" not in column:
                column=column.replace(' ','_')
                model_data=model_data+ f"""    {column}=models.()
"""
            else:
                column=column.replace("*","")
                column=column.replace("ForeignKey:","")
                column=column.replace(' ','_')
                source_table = column
                key_name= f"{source_table}_FK"
                model_data=f"""{model_data}    {key_name}=models.ForeignKey("{source_table}")
"""

    to_doc_w('models.py', model_data)


database_data_raw=readed_in_draw_io_file(filename)
write_yml_file(database_data_raw, 'raw_data.yml')
write_yml_file(database_data_raw, 'DB_data.yml')
flat_data = build_flatened_data(database_data_raw)
table_data = build_table_data(flat_data)            
write_yml_file(table_data, 'table_data.yml')
build_models(table_data,)



def build__init__(api_path):
    file_name = f"{api_path}/__init__.py"
    to_doc_w(file_name, '')

def build_serializers(table_data, api_path):
    output = '''from nautobot.core.api.serializers import ValidatedModelSerializer
from rest_framework.serializers import StringRelatedField
from PLUGIN_NAME_HERE.models import '''
    for table in table_data:
        table_name = table['name'].replace(' ','_')
        output = output+f"{table_name}, "
    output = output[:-2]
    for table in table_data:
        table_name = table['name'].replace(' ','_')
        output = output+f"""

class {table_name}Serializer(ValidatedModelSerializer):
        class Meta:
            model = {table_name}
            fields = ("pk", """
        for column in table['column']:
            column = column.replace(' ','_')
            output = output + f'"{column}", '
        output = f"""{output})"""
    filename = f"{api_path}/serializers.py"
    to_doc_w(filename, output)
    

def build_filters(table_name):
    output = """from nautobot.utilities.filters import BaseFilterSet
import django_filters
from django.utils import timezone
from .models import  """
    for table in table_data:
        table_name = table['name'].replace(' ','_')
        output = output+f"{table_name}, "
    output = output[:-2]
    for table in table_data:
        table_name = table['name'].replace(' ','_')
        output = output+f"""

class {table_name}FilterSet(django_filters.FilterSet):
    class Meta:
        model = {table_name}
        fields = ("pk", """
        for column in table['column']:
            column = column.replace(' ','_')
            output = output + f'"{column}", '


        output = f"""{output})"""
    filename = "filters.py"
    to_doc_w(filename, output)
    

def build_api_views(table_data, api_path):
    models = ''
    serializers=''
    filter_sets=''
    num = 0
    for each_table in table_data:
        table_name = each_table['name'].replace(' ','_')
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
from NAME OF PLUGIN.models import {models}
from .serializers import {serializers}
from NAME OF PLUGIN.filters import {filter_sets}
"""
    for each_table in table_data:
        table_name = each_table['name'].replace(' ','_')
        output=f"""{output}
    
class {table_name}ViewSet(ModelViewSet):
    queryset = {table_name}.objects.all()
    filterset_class = {table_name}FilterSet
    serializer_class = {table_name}Serializer
    """
    filename = f"{api_path}/views.py"
    to_doc_w(filename, output)    


def build_api_urls(table_data, api_path):
    output = """from nautobot.core.api.routers import OrderedDefaultRouter
from NAME OF PLUGIN HERE.api import views

router = OrderedDefaultRouter()

"""
    for each_table in table_data:
        table_name = each_table['name'].replace(' ','_')
        output=f"""{output}router.register("", views.{table_name}ViewSet)
"""
    output = f"{output}urlpatterns = router.urls"
    filename = f"{api_path}/urls.py"
    to_doc_w(filename, output)    


def build_api_data(table_data):
    api_path = "./api"
    if os.path.exists(api_path)==False:
        os.makedirs(api_path)
    build__init__(api_path)
    build_serializers(table_data, api_path)
    build_filters(table_data)
    build_api_views(table_data, api_path)
    build_api_urls(table_data, api_path)

build_api_data(table_data)        


