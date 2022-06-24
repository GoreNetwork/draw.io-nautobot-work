from typing import List
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

# filename = 'nautobot_robot_platform_data.drawio'
filename = "scrap_work.drawio"
project_name = filename.split('.')[0]

def normalize_column_name(column):
    if "***ForeignKey" in column:
        source_table = pull_source_table_for_fk(column)
        column= f"{source_table}_FK"
    if column == "PK" or column[-3:]=="_PK":
        return None
    column = column.replace(' ','')
    if "," in column:
        column = column.split(',')
        column = column[0]
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

def find_tables(table_data):
    tables = []
    for table in table_data:
        tables.append(table['name'])
    return tables

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

def normalize_column_name_for_models(column):
    if "***ForeignKey" in column:
        source_table = pull_source_table_for_fk(column)
        column= f"{source_table}_FK"
    if column == "PK" or column[-3:]=="_PK":
        return None
    column = column.replace(' ','')
    
    if "," in column:
        column = column.split(',')
    return column

def find_feild_types(table_data):
    feild_types_in_tables=[]
    for each in table_data:
        if 'relationship' in each:
            continue
        for column in each['column']:
            if "***ForeignKey" in column:
                continue
            column=normalize_column_name_for_models(column)
            if type(column)==list:
                key_name, feild_type =  column[0], column[1]
                feild_types_in_tables.append(feild_type)
    return feild_types_in_tables

            



def build_models(table_data):
    defaults_for_fields={
        'CharField': {"default_value_name":"max_length",
                        "default_value":"None"},
        "DateField": {"default_value_name":"auto_now","default_value":"False"},
        
    }
    feild_types_in_tables = find_feild_types(table_data)
    model_data = model_table_imports.render(feild_types_in_tables=feild_types_in_tables, defaults_for_fields=defaults_for_fields)
     
    pprint(feild_types_in_tables)
    for each in table_data:
        # pprint (each)
        if 'relationship' in each:
            continue
        table_name = normalise_table_name(each['name'])
        # print (table_name)
        model_data=model_data+model_class_head_template.render(table_name=table_name)
        for column in each['column']:
            feild_type="TextField"
            if "***ForeignKey" not in column:
                if " " in column:
                    print (table_name)
                column=normalize_column_name_for_models(column)
                if type(column)==list:
                    key_name, feild_type =  column[0], column[1]
                    print (key_name, feild_type)
                    feild_type=feild_type.replace(' ','')
                elif column==None:
                    continue
                else:
                    key_name = column
                model_data=model_data+model_class_body_non_foreign_key.render(column=key_name, feild_type=feild_type)
            else:
                source_table = pull_source_table_for_fk(column)
                key_name= f"{source_table}_FK"
                model_data=model_data+model_class_body_foreign_key.render(project_name=project_name, source_table=source_table, key_name=key_name)
                
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

    tables = find_tables(table_data)
    output = filter_imports.render(tables=tables)

    for table in table_data:
        columns = []
        for column in table['column']:
            column = normalize_column_name(column)
            if column==None:
                continue
            column = column.replace(' ','_')
            columns.append(column)
        table_name = normalise_table_name(table['name'])
        output = output+filter_classes.render(table_name=table_name, columns=columns)
    filename = f"{project_name}/filters.py"
    to_doc_w(filename, output)

def build_api_views(table_data, api_path):
    tables = find_tables(table_data)
    output = api_views_imports.render(tables=tables, project_name=project_name)

    for table in tables:
        table_name = normalise_table_name(table)
        output=output+api_classes_imports.render(table=table)
    
    filename = f"{api_path}/views.py"
    to_doc_w(filename, output)    

def build_api_urls(table_data, api_path):
    output = api_urls_imports.render(project_name=project_name)
    for each_table in table_data:
        table_name = normalise_table_name(each_table['name'])
        output = output+api_urls_classes.render(table_name=table_name)
    output = output+"urlpatterns = router.urls"
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


