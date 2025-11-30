from django.contrib import admin
from django_app.models import *

admin.site.register([User, TodoItem])