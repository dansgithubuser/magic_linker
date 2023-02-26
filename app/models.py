from . import sns

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import logging
import secrets
import string
import subprocess

logger = logging.getLogger('django.server')

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sns_topic_arn = models.TextField()

    def __str__(self):
        return f'{self.user} {self.sns_topic_arn}'

class Command(models.Model):
    name = models.TextField(primary_key=True)
    invocation = models.TextField()

    def __str__(self):
        return self.name

    def execute(self, request):
        execution = Execution.create(request, self.name, self.invocation)
        uri = request.build_absolute_uri(f'/execution/{execution.otp}/complete')
        sns.send(
            request.user.userinfo.sns_topic_arn,
            f'Complete execution of command "{self.name}".',
            f'Linkwizard {request.user.get_username()} has requested execution of command "{self.name}".',
            f'If you are not {request.user.get_username()}, please ignore this message.',
            f'Go here to complete execution: {uri}',
        )
        return execution

class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.ForeignKey(Command, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.command}'

class Execution(models.Model):
    command_name = models.TextField(db_index=True)
    command_invocation = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    user_email = models.TextField(db_index=True)
    otp = models.TextField(db_index=True)
    result = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True)

    def create(request, command_name, command_invocation):
        return Execution.objects.create(
            command_name=command_name,
            command_invocation=command_invocation,
            user=request.user,
            user_email=request.user.email,
            otp=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)),
        )

    def complete(self):
        try:
            self.result = subprocess.run(self.command_invocation.split()).returncode
        except Exception as e:
            logger.error(f'Error when completing execution {self.id}: {e}')
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.user_email} {self.command_name} {self.created_at} {self.completed_at} {self.result}'
