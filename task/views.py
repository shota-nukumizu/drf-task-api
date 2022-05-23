from requests import Response
from rest_framework import viewsets

from .serializers import TaskSerializer
from .models import Task


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer