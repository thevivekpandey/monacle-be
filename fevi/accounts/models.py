from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=30)
    account = models.ForeignKey(Account, related_name='teams', related_query_name='team', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class User(AbstractUser):
    USER = 'USER'
    ADMIN = 'ADMIN'
    ANALYST = 'ANALYST'
    USER_ROLE_CHOICES = (
        (ADMIN, 'ADMIN'),
        (ANALYST, 'ANALYST'),
        (USER, 'USER')
    )
    teams = models.ManyToManyField(Team, related_name='users', related_query_name='user')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='users', related_query_name='user')
    role = models.CharField(default=USER, max_length=100, choices=USER_ROLE_CHOICES)
    picture_url = models.URLField(blank=True, null=True)


# Create your models here.
class AccountSettings(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='settings',
                                   related_query_name='settings')
    all_users_team = models.OneToOneField(Team, on_delete=models.PROTECT, related_name='default_team',
                                          related_query_name='default_team')
    workspace = models.CharField(max_length=100, unique=True)
    admin = models.OneToOneField(User,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='admins',
                                 related_query_name='admin')
    gsuite_domain_only = models.BooleanField(default=False)
    gsuite_domain = models.CharField(max_length=100)


class DemoVisitor(models.Model):
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
