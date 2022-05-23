from requests import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .serializers import TaskSerializer
from .models import Task


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer