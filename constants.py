from jinja2 import Template


admin_table_imports=Template("""from django.contrib import admin
PLUGIN NAME HERE.models import {{ table_name_list | join(', ')}} """)

admin_class_template = Template("""
@admin.register({{table_name}})
class {{table_name}}Admin(admin.ModelAdmin):
    list_display = ( \"{{columns | join('", "')}}\")
    
""")