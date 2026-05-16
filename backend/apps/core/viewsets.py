from rest_framework import status, viewsets
from rest_framework.response import Response


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet that soft-deletes on destroy."""

    def perform_destroy(self, instance):
        instance.soft_delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
