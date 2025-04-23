from rest_framework import viewsets, mixins

from .models import Workflow
from .serializers import WorkflowSerializer


class WorkflowViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WorkflowSerializer

    def get_queryset(self):
        return Workflow.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
