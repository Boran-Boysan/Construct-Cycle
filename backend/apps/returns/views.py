from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReturnRequest, Refund
from .serializers import ReturnRequestSerializer, ReturnRequestCreateSerializer, RefundSerializer

class ReturnRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReturnRequestSerializer

    def get_queryset(self):
        return ReturnRequest.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnRequestCreateSerializer
        return ReturnRequestSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        obj = self.get_object()
        if obj.status == 'pending':
            obj.status = 'cancelled'
            obj.save()
        return Response({'message': 'Iptal edildi'})

class RefundViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RefundSerializer
    def get_queryset(self):
        return Refund.objects.filter(return_request__user=self.request.user)
