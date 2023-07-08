from . import sns

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import logging
import re
import secrets
import string

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
        uri = re.sub('^http:', 'https:', uri)
        logger.info(f'Executing command "{self.name}", sending confirmation to user "{request.user.get_username()}".')
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
        client_ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META['REMOTE_ADDR']
        assert re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', client_ip), f"IP doesn't look right: {client_ip}"
        return Execution.objects.create(
            command_name=command_name,
            command_invocation=command_invocation.format(
                client_ip=client_ip,
            ),
            user=request.user,
            user_email=request.user.email,
            otp=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)),
        )

    def complete(self):
        logger.info(f'Completing command "{self.command_name}" for user "{self.user.get_username()}".')
        with open(f'/mnt/executions/execution_{self.id}', 'w') as f:
            f.write(self.command_invocation)
        self.result = 0
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.user_email} {self.command_name} {self.created_at} {self.completed_at} {self.result}'
