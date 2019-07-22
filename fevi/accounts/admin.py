from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, Team


# Register your models here.

class AccountUser(User):
    class Meta:
        proxy = True


admin.site.register(User, UserAdmin)
admin.site.register(AccountUser)
admin.site.register(Account)
admin.site.register(Team)
