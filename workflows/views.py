from typing import override
from rest_framework.serializers import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Workflow
from .serializers import WorkflowSerializer


class WorkflowViewset(generics.ListCreateAPIView):
    serializer_class = WorkflowSerializer

    def get_queryset(self):
        return Workflow.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
