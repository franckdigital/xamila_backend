from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Max, F, Value
from django.db.models.functions import Concat

from .models_sgi import AccountOpeningRequest
from .serializers import ManagerContractSerializer, ManagerClientListItemSerializer


class IsManagerPermission(permissions.BasePermission):
    """Allow only SGI managers or staff"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, 'role', None)
        return bool(getattr(user, 'is_staff', False) or role in ('MANAGER', 'SGI_MANAGER'))


class ManagerContractsView(generics.ListAPIView):
    """List AccountOpeningRequest for SGIs managed by current manager"""
    serializer_class = ManagerContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerPermission]

    def get_queryset(self):
        user = self.request.user
        qs = AccountOpeningRequest.objects.select_related('sgi').order_by('-created_at')
        if getattr(user, 'is_staff', False):
            return qs
        return qs.filter(sgi__isnull=False, sgi__manager_email=user.email)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ManagerClientsView(APIView):
    """Aggregated list of clients who made requests to SGIs managed by current manager"""
    permission_classes = [permissions.IsAuthenticated, IsManagerPermission]

    def get(self, request):
        base_qs = AccountOpeningRequest.objects
        if not getattr(request.user, 'is_staff', False):
            base_qs = base_qs.filter(sgi__manager_email=request.user.email)

        agg_qs = base_qs.values('customer').annotate(
            customer_id=F('customer__id'),
            full_name=Concat(F('customer__first_name'), Value(' '), F('customer__last_name')),
            email=F('customer__email'),
            phone=F('customer__phone'),
            requests_count=Count('id'),
            last_request_at=Max('created_at')
        ).order_by('-last_request_at')

        data = list(agg_qs)
        serializer = ManagerClientListItemSerializer(data, many=True)
        return Response(serializer.data)
