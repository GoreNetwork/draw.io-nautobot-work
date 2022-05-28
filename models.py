"""Model definition for robot_platform_data."""
from django.db import models
from nautobot.core.models import BaseModel, OrganizationalModel, PrimaryModel
from datetime import datetime

model_type=PUT YOUR MODEL TYPE HERE!!

class Service_Catalog_Items(model_type):
    Primary_Key=models.   ()
    Name=models.   ()
    version=models.   ()
    status=models.   ()
    SMTP_required_(T/F)=models.   ()
    Remedy_required_(T/F)=models.   ()
    Description=models.   ()

class Network_Devices(model_type):
    Primary_Key=models.   ()
    Hardware_Type=models.   ()
    Device_Type=models.   ()
    Software=models.   ()

class Supported_Network_Devices(model_type):
    Primary_Key=models.   ()
    Service_Catalog_Items_PK=models.   ()
    Network_Devices_PK
=models.   ()

class NSO_Requirements(model_type):
    Primary_Key=models.   ()
    Service_Catalog_Items_PK=models.   ()
    NSO_Modes_PK=models.   ()
    cfs_prm_version=models.   ()
    ncs_version=models.   ()
    rfps_rpm_ver_PK=models.   ()

class cfs_rpm_version(model_type):
    Primary_key=models.   ()
    min=models.   ()
    max=models.   ()

class NSO_Packages(model_type):
    Primary_Key=models.   ()
    Name=models.   ()
    CFS_or_RFS=models.   ()
    min_ver=models.   ()
    max_ver=models.   ()

class Required_CFS_packages(model_type):
    PK=models.   ()
    NSO_Requirementts_PK=models.   ()
    CFS_Packages_PK=models.   ()

class services(model_type):
    PK=models.   ()
    Name=models.   ()
    min_ver=models.   ()
    max_ver=models.   ()

class Required_services(model_type):
    PK=models.   ()
    NSO_Requirementts_PK=models.   ()
    services_PK=models.   ()

class NSO_Settings(model_type):
    PK=models.   ()
    CFS_or_RFS=models.   ()
    Setting=models.   ()

class Required_rfs_neds(model_type):
    PK=models.   ()
    NSO_Requirementts_PK=models.   ()
    NSO_Settings_PK=models.   ()

class service_domains(model_type):
    PK=models.   ()
    Domain=models.   ()
    region=models.   ()

class Required_service_domains(model_type):
    PK=models.   ()
    service_domain_PK=models.   ()
    Service_Catalog_PK=models.   ()

class NSO_required_Modes(model_type):
    PK=models.   ()
    Mode=models.   ()
    NSO_Requirements_PK=models.   ()

class rfs_rpm_ver(model_type):
    PK=models.   ()
    min=models.   ()
    max=models.   ()

class Service_Catalog_Item_Changes(model_type):
    PK=models.   ()
    changes_text=models.   ()
    Serivce_Catalog_PK=models.   ()

class NIDM_requirements(model_type):
    Primary_Key=models.   ()
    Service_Catalog_Items_Pk=models.   ()
    Item_3=models.   ()

class NIDM_Services(model_type):
    Primary_Key=models.   ()
    name=models.   ()
    minimum_version=models.   ()
    maximum_version=models.   ()

class NIMD_Required_Services(model_type):
    Primary_Key=models.   ()
    NIDM_requirements_PK=models.   ()
    NIDM_Services_PK=models.   ()
