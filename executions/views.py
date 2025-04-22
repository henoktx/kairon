from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .services.start_execution import start_execution
from .models import Execution
from .serializers import ExecutionSerializer


class ExecutionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = ExecutionSerializer

    def get_queryset(self):
        return Execution.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        try:
            result = start_execution(execution_id=pk)
            return Response(result, status=status.HTTP_201_CREATED)
        except RuntimeError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
