from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin

from .database import MYSQL_DATABASE_URL
from .models.users import APIUser

site = AdminSite(settings=Settings(database_url=MYSQL_DATABASE_URL))


@site.register_admin
class APIUserAdmin(admin.ModelAdmin):
    page_schema = 'Users'
    # set model
    model = APIUser
