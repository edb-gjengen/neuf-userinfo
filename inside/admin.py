from django.contrib import admin

# Register your models here.
from inside.models import *


admin.site.register(InsideGroup)
admin.site.register(InsideUser)