from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Execution
from .serializers import ExecutionSerializer
from .services.reset_execution import reset_execution
from .services.start_execution import start_execution


class ExecutionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExecutionSerializer

    def get_queryset(self):
        return Execution.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        try:
            start_execution(execution_id=pk)
            return Response(status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def reset(self, request, pk=None):
        try:
            reset_execution(execution_id=pk)
            return Response(status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
