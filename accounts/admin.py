from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
admin.site.site_header = "Yermo: administración"
admin.site.site_title = "Yermo"
admin.site.index_title = "Base de datos"
