from jinja2 import Template


admin_table_imports=Template("""from django.contrib import admin
from {{project_name}}.models import {{ table_name_list | join(', ')}} 
""")

admin_class_template = Template("""
@admin.register({{table_name}})
class {{table_name}}Admin(admin.ModelAdmin):
    list_display = ( \"{{columns | join('", "')}}\")
    
""")

model_table_imports=Template('''from django.db import models
from nautobot.core.models import BaseModel
from nautobot.core.models.generics import OrganizationalModel, PrimaryModel
from datetime import datetime

model_type=PUT YOUR MODEL TYPE HERE!!
''')

model_class_head_template=Template("""

class {{table_name}}(model_type):
""")

model_class_body_non_foreign_key=Template("""
    {{ column }}=models.()
""")
model_class_body_foreign_key=Template("""
    {{ key_name }}=models.ForeignKey("{{source_table}}", on_delete=models.RESTRICT)
""")

seralizer_imports=Template("""from nautobot.core.api.serializers import ValidatedModelSerializer
from rest_framework.serializers import StringRelatedField
from {{ project_name }}.models import {{ table_names | join(', ')}} 

""")

serlizer_classes=Template("""
class {{table_name}}Serializer(ValidatedModelSerializer):
        class Meta:
            model = {{table_name}}
            fields = ("pk", "{{ columns | join('", "')}}")

""")

filter_imports=Template("""from nautobot.utilities.filters import BaseFilterSet
import django_filters
from django.utils import timezone
from .models import  {{ tables | join(', ')}}

""")
filter_classes=Template("""
class {{table_name}}FilterSet(django_filters.FilterSet):
    class Meta:
        model = {{ table_name }}
        fields = ("{{ columns | join('", "')}}")

""")

api_views_imports=Template("""from nautobot.core.api.views import ModelViewSet
from {{project_name}}.models import {{ tables | join(', ')}}
from .serializers import {{ tables | join('Serializer, ')}}Serializer
from {{project_name}}.filters import {{ tables | join('FilterSet, ')}}FilterSet

""")

api_classes_imports=Template("""
class {{ table }}ViewSet(ModelViewSet):
    queryset = {{ table }}.objects.all()
    filterset_class = {{ table }}FilterSet
    serializer_class = {{ table }}Serializer

""")

api_urls_imports=Template("""from nautobot.core.api.routers import OrderedDefaultRouter
from {{project_name}}.api import views

router = OrderedDefaultRouter()

""")

api_urls_classes=Template("""router.register("{{ table_name }}", views.{{ table_name }}ViewSet)

""")

