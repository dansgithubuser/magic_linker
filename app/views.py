from . import models

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from datetime import timedelta
import json

def _message(request, message, status):
    return render(
        request,
        'message.html',
        {'message': message},
        status=status,
    )

@login_required
def home(request):
    commands = models.Command.objects.filter(permission__user=request.user)
    executions = (
        models.Execution.objects
            .filter(user=request.user)
            .order_by('-id')
            [:10]
    )
    return render(request, 'home.html', {
        'commands': commands,
        'executions': executions,
    })
home.route = ''

@login_required
@require_http_methods(['POST'])
def command_execute(request, name):
    if not models.Permission.objects.get(user=request.user, command=name):
        return HttpResponse(status=401)
    hour_ago = timezone.now() - timedelta(hours=1)
    prev = (
        models.Execution.objects
            .filter(
                command_name=name,
                user=request.user,
                created_at__gte=hour_ago,
                completed_at__isnull=True,
            )
            .first()
    )
    if prev:
        return _message(request, 'Incomplete execution for this command already exists.', 429)
    command = models.Command.objects.get(name=name)
    command.execute(request)
    return redirect('/')
command_execute.route = 'command/<str:name>/execute'

@login_required
@csrf_exempt
def execution_complete(request, otp):
    execution = models.Execution.objects.get(otp=otp)
    if not execution or execution.user != request.user:
        return _message(request, 'No such execution.', 404)
    if execution.completed_at:
        return _message(request, 'Execution has already been completed.', 400)
    hour_ago = timezone.now() - timedelta(hours=1)
    if execution.created_at < hour_ago:
        return _message(request, 'Execution has expired.', 400)
    execution.complete()
    return redirect('/')
execution_complete.route = 'execution/<str:otp>/complete'
