from jinja2 import Template


admin_table_imports = Template(
    """from django.contrib import admin
from {{project_name}}.models import {{ table_name_list | join(', ')}} 
"""
)

admin_class_template = Template(
    """
@admin.register({{table_name}})
class {{table_name}}Admin(admin.ModelAdmin):
    list_display = ( \"{{columns | join('", "')}}\",)
    
"""
)

model_table_imports = Template(
    """from django.db import models
from nautobot.core.models import BaseModel
from nautobot.core.models.generics import OrganizationalModel, PrimaryModel
from datetime import datetime

#Default values for field uses, these are defined in build_db under build_models, defaults_for_fields{% for feild_types_in_table in feild_types_in_tables %}
{{ feild_types_in_table }}_default={{ defaults_for_fields[feild_types_in_table]['default_value']}}{% endfor %}
model_type=PrimaryModel
default_on_delete = models.RESTRICT
"""
)

model_class_head_template = Template(
    """

class {{table_name}}(model_type):
"""
)

model_class_body_non_foreign_key = Template(
    """{% if feild_type in defaults_for_fields %}
    {{ column }}=models.{{feild_type}}({{defaults_for_fields[feild_type]["default_value_name"]}}={{feild_type}}_default){%- else %}
    {{ column }}=models.{{feild_type}}(){%- endif %}
"""
)

model_class_body_foreign_key = Template(
    """
    {{ key_name }}=models.ForeignKey("{{ project_name }}.{{source_table}}", on_delete=default_on_delete)
"""
)

seralizer_imports = Template(
    """from nautobot.core.api.serializers import ValidatedModelSerializer
from rest_framework.serializers import StringRelatedField
from {{ project_name }}.models import {{ table_names | join(', ')}} 

"""
)

serlizer_classes = Template(
    """
class {{table_name}}Serializer(ValidatedModelSerializer):
        class Meta:
            model = {{table_name}}
            fields = ("pk", "{{ columns | join('", "')}}")

"""
)

filter_imports = Template(
    """from nautobot.utilities.filters import BaseFilterSet
import django_filters
from django.utils import timezone
from .models import  {{ tables | join(', ')}}

"""
)
filter_classes = Template(
    """
class {{table_name}}FilterSet(django_filters.FilterSet):
    class Meta:
        model = {{ table_name }}
        fields = ("{{ columns | join('", "')}}",)

"""
)

api_views_imports = Template(
    """from nautobot.core.api.views import ModelViewSet
from {{project_name}}.models import {{ tables | join(', ')}}
from .serializers import {{ tables | join('Serializer, ')}}Serializer
from {{project_name}}.filters import {{ tables | join('FilterSet, ')}}FilterSet

"""
)

api_classes_imports = Template(
    """
class {{ table }}ViewSet(ModelViewSet):
    queryset = {{ table }}.objects.all()
    filterset_class = {{ table }}FilterSet
    serializer_class = {{ table }}Serializer

"""
)

api_urls_imports = Template(
    """from nautobot.core.api.routers import OrderedDefaultRouter
from {{project_name}}.api import views

router = OrderedDefaultRouter()

"""
)

api_urls_classes = Template(
    """router.register("{{ table_name }}", views.{{ table_name }}ViewSet)

"""
)

setup_file = Template(
    """from setuptools import find_packages, setup

setup(
    name='{{project_name}}',
    version='0.1',
    description='{{plugin_description}}',
    author='{{plugin_author}}',
    packages=find_packages(),
    include_package_data=True,
)

"""
)

init_file = Template(
    """

from nautobot.extras.plugins import PluginConfig

class {{project_name}}Config(PluginConfig):

    name = "{{project_name}}"
    verbose_name = "{{project_name}}"
    author = "{{plugin_author}}"
    description = "{{project_name}}"
    base_url = "{{project_name}}"
    required_settings = []
    min_version = "1.1.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = {{project_name}}Config

"""
)

jobs_header = Template(
    """from nautobot.extras.jobs import IntegerVar, Job
from yaml.loader import SafeLoader
from {{project_name}}.models import {{ tables | join(', ')}}


"""
)

jobs_get_or_create = Template(
    """def update_{{table_name}}_get_or_create({{ columns | join(', ')}}):
    table_update, created = {{table_name}}.objects.get_or_create({% for column in columns %}
        {{column}}={{column}},{% endfor %})

    if created:
        self.log_success( f"Added to {{table_name}}: {{ log_message}}")
    else:
        self.log_info( f"Already Exists in {{table_name}}: {{ log_message }}")

    return table_update


"""
)
