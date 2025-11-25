"""Views for checklists"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import ChecklistTemplate, ChecklistResponse
from .serializers import (
    ChecklistTemplateSerializer,
    ChecklistResponseSerializer,
    ChecklistResponseCreateSerializer
)
from .services import ChecklistService
import logging

logger = logging.getLogger(__name__)


class ChecklistTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for checklist templates"""
    queryset = ChecklistTemplate.objects.all()
    serializer_class = ChecklistTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehicle_type', 'is_system_template']
    search_fields = ['code', 'name']
    
    def get_permissions(self):
        """Only admins can create/update/delete templates"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def by_vehicle_type(self, request):
        """Get templates grouped by vehicle type"""
        vehicle_type = request.query_params.get('vehicle_type')
        
        if vehicle_type:
            templates = self.get_queryset().filter(vehicle_type=vehicle_type)
        else:
            templates = self.get_queryset()
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class ChecklistResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for checklist responses"""
    queryset = ChecklistResponse.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template', 'asset', 'work_order', 'passed', 'completed_by']
    search_fields = ['operator_name']
    ordering_fields = ['completed_at', 'score']
    ordering = ['-completed_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChecklistResponseCreateSerializer
        return ChecklistResponseSerializer
    
    def get_queryset(self):
        """Filter checklists based on user role"""
        user = self.request.user
        queryset = ChecklistResponse.objects.all().select_related(
            'template', 'asset', 'work_order', 'completed_by'
        )
        
        # ADMIN and SUPERVISOR see all
        if user.can_view_all_resources():
            return queryset
        
        # OPERADOR sees only their completed checklists
        return queryset.filter(completed_by=user)
    
    def perform_create(self, serializer):
        """Set completed_by on creation and generate PDF"""
        checklist = serializer.save(completed_by=self.request.user)
        
        # Generate PDF and upload to Cloud Storage
        try:
            ChecklistService.generate_and_upload_pdf(checklist)
        except Exception as e:
            logger.error(f"Error generating PDF for checklist {checklist.id}: {e}")
            # Don't fail the request if PDF generation fails
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Get signed URL for checklist PDF"""
        checklist = self.get_object()
        
        if not checklist.pdf_url:
            return Response(
                {
                    'error': 'PDF no disponible',
                    'message': 'El PDF no se generó automáticamente. Use el endpoint /regenerate_pdf/ para generarlo.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get signed URL for secure access
        signed_url = ChecklistService.get_pdf_signed_url(checklist)
        
        if not signed_url:
            return Response(
                {'error': 'Error generando URL de acceso al PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({'pdf_url': signed_url})
    
    @action(detail=True, methods=['post'])
    def regenerate_pdf(self, request, pk=None):
        """
        Manually regenerate PDF for a checklist
        Useful when automatic generation failed or LibreOffice wasn't available
        """
        checklist = self.get_object()
        
        try:
            pdf_url = ChecklistService.generate_and_upload_pdf(checklist)
            
            if pdf_url:
                return Response({
                    'message': 'PDF generado exitosamente',
                    'pdf_url': pdf_url
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'No se pudo generar el PDF',
                    'message': 'Verifique que LibreOffice esté instalado y que el servicio de almacenamiento esté configurado'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error regenerating PDF for checklist {checklist.id}: {e}", exc_info=True)
            return Response({
                'error': 'Error al generar PDF',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_asset(self, request):
        """Get checklists for specific asset"""
        asset_id = request.query_params.get('asset_id')
        
        if not asset_id:
            return Response(
                {'error': 'asset_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.filter_queryset(
            self.get_queryset().filter(asset_id=asset_id)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def complete(self, request):
        """
        Complete a checklist with vehicle_type validation
        Endpoint: POST /api/v1/checklists/responses/complete/
        """
        serializer = ChecklistResponseCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Additional validation
                template = serializer.validated_data['template']
                asset = serializer.validated_data['asset']
                
                is_valid, error_msg = ChecklistService.validate_checklist_for_asset(template, asset)
                if not is_valid:
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create checklist
                checklist = serializer.save(completed_by=request.user)
                
                # Generate PDF
                try:
                    ChecklistService.generate_and_upload_pdf(checklist)
                except Exception as e:
                    logger.error(f"Error generating PDF: {e}")
                
                # Return response
                response_serializer = ChecklistResponseSerializer(checklist)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
            except DjangoValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get checklist statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total': queryset.count(),
            'passed': queryset.filter(passed=True).count(),
            'failed': queryset.filter(passed=False).count(),
            'average_score': 0,
            'by_template': {}
        }
        
        # Calculate average score
        if queryset.exists():
            total_score = sum(c.score for c in queryset)
            stats['average_score'] = round(total_score / queryset.count(), 2)
        
        # By template
        templates = ChecklistTemplate.objects.filter(is_system_template=True)
        for template in templates:
            template_responses = queryset.filter(template=template)
            stats['by_template'][template.code] = {
                'name': template.name,
                'count': template_responses.count(),
                'passed': template_responses.filter(passed=True).count(),
                'failed': template_responses.filter(passed=False).count()
            }
        
        return Response(stats)
