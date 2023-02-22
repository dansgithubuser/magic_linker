from django.contrib.auth.models import User
from django.db import models

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sns_topic_arn = models.TextField()

class Command(models.Model):
    name = models.TextField(primary_key=True)
    invocation = models.TextField()

class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.ForeignKey(Command , on_delete=models.CASCADE)

class Execution(models.Model):
    command = models.TextField()
    result = models.IntegerField(null=True)
    otp = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
