from django.contrib import admin

# Register your models here.
from .models import Question, DataSource

admin.site.register(DataSource)
admin.site.register(Question)