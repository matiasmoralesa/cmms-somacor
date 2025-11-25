"""
Django management command to initialize roles and permissions
Run: python manage.py init_roles_permissions
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import Role, Permission


class Command(BaseCommand):
    help = 'Initialize roles and permissions for CMMS system'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing roles and permissions...')
        
        # Create roles
        roles_created = self.create_roles()
        
        # Create permissions
        permissions_created = self.create_permissions()
        
        # Assign permissions to roles
        self.assign_permissions()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully initialized:'
            f'\n   - {roles_created} roles'
            f'\n   - {permissions_created} permissions'
        ))
    
    def create_roles(self):
        """Create the 3 system roles"""
        roles_data = [
            {
                'name': Role.ADMIN,
                'description': 'Administrador con acceso completo al sistema'
            },
            {
                'name': Role.SUPERVISOR,
                'description': 'Supervisor con acceso de gestión operativa'
            },
            {
                'name': Role.OPERADOR,
                'description': 'Operador con acceso limitado a tareas asignadas'
            },
        ]
        
        created = 0
        for role_data in roles_data:
            role, created_flag = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created_flag:
                created += 1
                self.stdout.write(f'  Created role: {role.get_name_display()}')
            else:
                self.stdout.write(f'  Role already exists: {role.get_name_display()}')
        
        return created
    
    def create_permissions(self):
        """Create all system permissions"""
        permissions_data = [
            # Dashboard permissions
            {'code': 'view_dashboard', 'name': 'Ver Dashboard', 'module': 'dashboard'},
            {'code': 'view_all_stats', 'name': 'Ver Estadísticas Completas', 'module': 'dashboard'},
            
            # Asset permissions
            {'code': 'view_all_assets', 'name': 'Ver Todos los Equipos', 'module': 'assets'},
            {'code': 'view_assigned_assets', 'name': 'Ver Equipos Asignados', 'module': 'assets'},
            {'code': 'create_asset', 'name': 'Crear Equipo', 'module': 'assets'},
            {'code': 'edit_asset', 'name': 'Editar Equipo', 'module': 'assets'},
            {'code': 'delete_asset', 'name': 'Eliminar Equipo', 'module': 'assets'},
            {'code': 'upload_asset_documents', 'name': 'Subir Documentos de Equipo', 'module': 'assets'},
            
            # Work Order permissions
            {'code': 'view_all_work_orders', 'name': 'Ver Todas las OT', 'module': 'work_orders'},
            {'code': 'view_assigned_work_orders', 'name': 'Ver OT Asignadas', 'module': 'work_orders'},
            {'code': 'create_work_order', 'name': 'Crear OT', 'module': 'work_orders'},
            {'code': 'assign_work_order', 'name': 'Asignar OT', 'module': 'work_orders'},
            {'code': 'edit_work_order', 'name': 'Editar OT', 'module': 'work_orders'},
            {'code': 'complete_work_order', 'name': 'Completar OT', 'module': 'work_orders'},
            {'code': 'cancel_work_order', 'name': 'Cancelar OT', 'module': 'work_orders'},
            
            # Checklist permissions
            {'code': 'view_all_checklists', 'name': 'Ver Todos los Checklists', 'module': 'checklists'},
            {'code': 'view_assigned_checklists', 'name': 'Ver Checklists Asignados', 'module': 'checklists'},
            {'code': 'complete_checklist', 'name': 'Completar Checklist', 'module': 'checklists'},
            {'code': 'download_checklist_pdf', 'name': 'Descargar PDF de Checklist', 'module': 'checklists'},
            
            # Failure Report permissions
            {'code': 'report_failure', 'name': 'Reportar Falla', 'module': 'failures'},
            {'code': 'view_all_failure_reports', 'name': 'Ver Todos los Reportes de Falla', 'module': 'failures'},
            {'code': 'view_own_failure_reports', 'name': 'Ver Reportes Propios', 'module': 'failures'},
            
            # Maintenance Plan permissions
            {'code': 'view_maintenance_plans', 'name': 'Ver Planes de Mantenimiento', 'module': 'maintenance'},
            {'code': 'create_maintenance_plan', 'name': 'Crear Plan de Mantenimiento', 'module': 'maintenance'},
            {'code': 'edit_maintenance_plan', 'name': 'Editar Plan de Mantenimiento', 'module': 'maintenance'},
            {'code': 'delete_maintenance_plan', 'name': 'Eliminar Plan de Mantenimiento', 'module': 'maintenance'},
            {'code': 'view_calendar', 'name': 'Ver Calendario', 'module': 'maintenance'},
            
            # Inventory permissions
            {'code': 'view_inventory', 'name': 'Ver Inventario', 'module': 'inventory'},
            {'code': 'manage_inventory', 'name': 'Gestionar Inventario', 'module': 'inventory'},
            
            # Prediction permissions
            {'code': 'view_predictions', 'name': 'Ver Predicciones', 'module': 'predictions'},
            {'code': 'view_alerts', 'name': 'Ver Alertas', 'module': 'predictions'},
            
            # Reports permissions
            {'code': 'view_reports', 'name': 'Ver Reportes', 'module': 'reports'},
            {'code': 'generate_reports', 'name': 'Generar Reportes', 'module': 'reports'},
            {'code': 'view_kpis', 'name': 'Ver KPIs', 'module': 'reports'},
            
            # Administration permissions (ADMIN only)
            {'code': 'manage_users', 'name': 'Gestionar Usuarios', 'module': 'administration'},
            {'code': 'manage_roles', 'name': 'Gestionar Roles', 'module': 'administration'},
            {'code': 'manage_system_config', 'name': 'Gestionar Configuración', 'module': 'administration'},
            {'code': 'view_audit_logs', 'name': 'Ver Logs de Auditoría', 'module': 'administration'},
        ]
        
        created = 0
        for perm_data in permissions_data:
            permission, created_flag = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'module': perm_data['module']
                }
            )
            if created_flag:
                created += 1
        
        self.stdout.write(f'  Created {created} new permissions')
        return created
    
    def assign_permissions(self):
        """Assign permissions to roles based on profile matrix"""
        admin_role = Role.objects.get(name=Role.ADMIN)
        supervisor_role = Role.objects.get(name=Role.SUPERVISOR)
        operador_role = Role.objects.get(name=Role.OPERADOR)
        
        # ADMIN gets ALL permissions
        admin_permissions = Permission.objects.all()
        admin_role.permissions.set(admin_permissions)
        self.stdout.write(f'  Assigned {admin_permissions.count()} permissions to ADMIN')
        
        # SUPERVISOR permissions
        supervisor_permission_codes = [
            # Dashboard
            'view_dashboard', 'view_all_stats',
            # Assets
            'view_all_assets', 'create_asset', 'edit_asset', 'upload_asset_documents',
            # Work Orders
            'view_all_work_orders', 'create_work_order', 'assign_work_order',
            'edit_work_order', 'complete_work_order',
            # Checklists
            'view_all_checklists', 'complete_checklist', 'download_checklist_pdf',
            # Failures
            'report_failure', 'view_all_failure_reports',
            # Maintenance
            'view_maintenance_plans', 'create_maintenance_plan', 'edit_maintenance_plan',
            'view_calendar',
            # Inventory
            'view_inventory', 'manage_inventory',
            # Predictions
            'view_predictions', 'view_alerts',
            # Reports
            'view_reports', 'generate_reports', 'view_kpis',
        ]
        supervisor_permissions = Permission.objects.filter(code__in=supervisor_permission_codes)
        supervisor_role.permissions.set(supervisor_permissions)
        self.stdout.write(f'  Assigned {supervisor_permissions.count()} permissions to SUPERVISOR')
        
        # OPERADOR permissions (limited)
        operador_permission_codes = [
            # Assets (only assigned)
            'view_assigned_assets',
            # Work Orders (only assigned)
            'view_assigned_work_orders', 'complete_work_order',
            # Checklists (only assigned)
            'view_assigned_checklists', 'complete_checklist', 'download_checklist_pdf',
            # Failures
            'report_failure', 'view_own_failure_reports',
        ]
        operador_permissions = Permission.objects.filter(code__in=operador_permission_codes)
        operador_role.permissions.set(operador_permissions)
        self.stdout.write(f'  Assigned {operador_permissions.count()} permissions to OPERADOR')
