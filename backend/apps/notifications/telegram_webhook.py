"""
Telegram Webhook Handler for Somacorbot
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from functools import wraps
import json
from .telegram_service import get_telegram_service

logger = logging.getLogger(__name__)
User = get_user_model()


def require_linked_user(func):
    """Decorator to require linked user for command"""
    @wraps(func)
    def wrapper(chat_id, user_info, telegram_service, *args, **kwargs):
        user = User.objects.filter(telegram_chat_id=str(chat_id)).first()
        if not user:
            telegram_service.send_message(
                chat_id=str(chat_id),
                text="❌ <b>Cuenta no vinculada</b>\n\nDebes vincular tu cuenta primero. Usa /link para ver las instrucciones.",
                parse_mode='HTML'
            )
            return
        return func(chat_id, user_info, telegram_service, user, *args, **kwargs)
    return wrapper


def require_role(allowed_roles):
    """Decorator to require specific role for command"""
    def decorator(func):
        @wraps(func)
        def wrapper(chat_id, user_info, telegram_service, user, *args, **kwargs):
            if not hasattr(user, 'role') or user.role not in allowed_roles:
                telegram_service.send_message(
                    chat_id=str(chat_id),
                    text="🚫 <b>Acceso Denegado</b>\n\nNo tienes permisos para usar este comando.",
                    parse_mode='HTML'
                )
                return
            return func(chat_id, user_info, telegram_service, user, *args, **kwargs)
        return wrapper
    return decorator


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Handle incoming updates from Telegram
    """
    try:
        update = json.loads(request.body.decode('utf-8'))
        
        # Extract message
        message = update.get('message')
        if not message:
            return JsonResponse({'ok': True})
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user_info = message.get('from', {})
        
        if not chat_id:
            return JsonResponse({'ok': True})
        
        # Handle commands
        if text.startswith('/'):
            handle_command(chat_id, text, user_info)
        
        return JsonResponse({'ok': True})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)



def handle_command(chat_id, text, user_info):
    """Handle bot commands"""
    telegram_service = get_telegram_service()
    command = text.split()[0].lower()
    
    # Public commands (no authentication required)
    if command == '/start':
        handle_start(chat_id, user_info, telegram_service)
    elif command == '/help':
        handle_help(chat_id, telegram_service)
    elif command == '/link':
        handle_link_instructions(chat_id, telegram_service)
    
    # Commands requiring authentication
    elif command == '/status':
        handle_status(chat_id, telegram_service)
    elif command == '/test':
        handle_test(chat_id, telegram_service)
    elif command == '/unlink':
        handle_unlink(chat_id, telegram_service)
    elif command == '/equipos':
        handle_equipos(chat_id, user_info, telegram_service)
    elif command == '/ordenes':
        handle_ordenes(chat_id, user_info, telegram_service)
    elif command == '/pendientes':
        handle_pendientes(chat_id, user_info, telegram_service)
    elif command == '/alertas':
        handle_alertas(chat_id, user_info, telegram_service)
    elif command == '/kpis':
        handle_kpis(chat_id, user_info, telegram_service)
    else:
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❓ Comando no reconocido. Usa /help para ver los comandos disponibles."
        )


def handle_start(chat_id, user_info, telegram_service):
    """Handle /start command"""
    first_name = user_info.get('first_name', 'Usuario')
    username = user_info.get('username', '')
    
    message = f"""
👋 <b>¡Hola {first_name}!</b>

Bienvenido a <b>Somacorbot</b>, el bot oficial del Sistema CMMS de Somacor.

🆔 <b>Tu Chat ID es:</b> <code>{chat_id}</code>

📋 <b>Para vincular tu cuenta:</b>
1. Copia tu Chat ID (toca para copiar)
2. Ingresa a la aplicación web CMMS
3. Ve a tu perfil → Notificaciones
4. Pega tu Chat ID y vincula

💡 <b>Comandos disponibles:</b>
/help - Ver ayuda completa
/link - Instrucciones de vinculación
/status - Ver estado de tu cuenta
/test - Probar notificaciones

¿Necesitas ayuda? Usa /help
"""
    
    telegram_service.send_message(
        chat_id=str(chat_id),
        text=message.strip(),
        parse_mode='HTML'
    )


def handle_help(chat_id, telegram_service):
    """Handle /help command"""
    message = """
📚 <b>Ayuda de Somacorbot</b>

<b>🔓 Comandos Públicos:</b>
/start - Iniciar el bot y obtener tu Chat ID
/help - Mostrar esta ayuda
/link - Ver instrucciones de vinculación

<b>👤 Comandos de Usuario:</b>
/status - Ver estado de tu cuenta
/test - Enviar notificación de prueba
/ordenes - Ver tus órdenes de trabajo
/pendientes - Ver órdenes pendientes
/alertas - Ver alertas recientes
/unlink - Desvincular tu cuenta

<b>📊 Comandos de Información:</b>
/equipos - Ver lista de equipos
/kpis - Ver métricas del sistema

<b>¿Cómo funciona?</b>

1️⃣ Obtén tu Chat ID con /start
2️⃣ Vincula tu cuenta en la app web
3️⃣ Configura tus preferencias
4️⃣ ¡Usa los comandos!

<b>Tipos de notificaciones:</b>
📋 Órdenes de trabajo asignadas
⚙️ Mantenimiento preventivo
📦 Alertas de inventario
🔮 Predicciones de fallas
🚨 Alertas críticas

<b>¿Problemas?</b>
Contacta al administrador del sistema.
"""
    
    telegram_service.send_message(
        chat_id=str(chat_id),
        text=message.strip(),
        parse_mode='HTML'
    )



def handle_link_instructions(chat_id, telegram_service):
    """Handle /link command"""
    message = f"""
🔗 <b>Instrucciones de Vinculación</b>

<b>Paso 1:</b> Copia tu Chat ID
🆔 Tu Chat ID: <code>{chat_id}</code>

<b>Paso 2:</b> Ingresa a la aplicación web
🌐 Abre el sistema CMMS en tu navegador

<b>Paso 3:</b> Ve a Notificaciones
👤 Perfil → Configuración → Notificaciones

<b>Paso 4:</b> Vincula tu cuenta
📱 Pega tu Chat ID y haz clic en "Vincular Telegram"

<b>Paso 5:</b> Configura preferencias
⚙️ Selecciona qué notificaciones quieres recibir

✅ Una vez vinculado, recibirás un mensaje de confirmación aquí.

💡 <b>Tip:</b> Puedes usar /test para verificar que todo funciona correctamente.
"""
    
    telegram_service.send_message(
        chat_id=str(chat_id),
        text=message.strip(),
        parse_mode='HTML'
    )


def handle_status(chat_id, telegram_service):
    """Handle /status command"""
    # Check if user is linked
    try:
        user = User.objects.filter(telegram_chat_id=str(chat_id)).first()
        
        if user:
            message = f"""
✅ <b>Cuenta Vinculada</b>

👤 <b>Usuario:</b> {user.get_full_name() or user.username}
📧 <b>Email:</b> {user.email}
🆔 <b>Chat ID:</b> <code>{chat_id}</code>

<b>Estado:</b> Activo ✓

Estás recibiendo notificaciones del sistema CMMS.

💡 Usa /test para enviar una notificación de prueba.
🔓 Usa /unlink para desvincular tu cuenta.
"""
        else:
            message = f"""
❌ <b>Cuenta No Vinculada</b>

🆔 <b>Tu Chat ID:</b> <code>{chat_id}</code>

No tienes una cuenta vinculada al sistema CMMS.

🔗 Usa /link para ver las instrucciones de vinculación.
"""
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al verificar el estado. Intenta nuevamente."
        )


def handle_test(chat_id, telegram_service):
    """Handle /test command"""
    try:
        user = User.objects.filter(telegram_chat_id=str(chat_id)).first()
        
        if user:
            telegram_service.send_notification(
                chat_id=str(chat_id),
                notification_type='SYSTEM',
                title='🧪 Notificación de Prueba',
                message='Si ves este mensaje, tu configuración de Telegram está funcionando correctamente. ¡Todo listo para recibir notificaciones del sistema CMMS!',
                priority='MEDIUM'
            )
        else:
            message = f"""
❌ <b>Cuenta No Vinculada</b>

Para enviar notificaciones de prueba, primero debes vincular tu cuenta.

🆔 <b>Tu Chat ID:</b> <code>{chat_id}</code>

🔗 Usa /link para ver las instrucciones.
"""
            telegram_service.send_message(
                chat_id=str(chat_id),
                text=message.strip(),
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Error sending test: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al enviar notificación de prueba."
        )


def handle_unlink(chat_id, telegram_service):
    """Handle /unlink command"""
    try:
        user = User.objects.filter(telegram_chat_id=str(chat_id)).first()
        
        if user:
            user.telegram_chat_id = None
            user.save(update_fields=['telegram_chat_id'])
            
            message = """
✅ <b>Cuenta Desvinculada</b>

Tu cuenta ha sido desvinculada exitosamente.

Ya no recibirás notificaciones del sistema CMMS en este chat.

🔗 Puedes volver a vincular tu cuenta en cualquier momento usando /link
"""
        else:
            message = """
ℹ️ <b>No hay cuenta vinculada</b>

No tienes ninguna cuenta vinculada a este chat.

🔗 Usa /link si deseas vincular una cuenta.
"""
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error unlinking: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al desvincular la cuenta."
        )



@require_linked_user
def handle_equipos(chat_id, user_info, telegram_service, user):
    """Handle /equipos command - List assets"""
    from apps.assets.models import Asset
    
    try:
        assets = Asset.objects.filter(status='ACTIVE').order_by('vehicle_type', 'name')[:10]
        
        if not assets:
            message = """
📦 <b>Equipos</b>

No hay equipos activos registrados.
"""
        else:
            message = "📦 <b>Equipos Activos</b>\n\n"
            
            current_type = None
            for asset in assets:
                if asset.vehicle_type != current_type:
                    current_type = asset.vehicle_type
                    message += f"\n<b>{asset.get_vehicle_type_display()}:</b>\n"
                
                message += f"• {asset.name} ({asset.asset_code})\n"
            
            if Asset.objects.filter(status='ACTIVE').count() > 10:
                message += f"\n<i>Mostrando 10 de {Asset.objects.filter(status='ACTIVE').count()} equipos</i>"
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in /equipos: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al obtener la lista de equipos."
        )


@require_linked_user
def handle_ordenes(chat_id, user_info, telegram_service, user):
    """Handle /ordenes command - User's work orders"""
    from apps.work_orders.models import WorkOrder
    
    try:
        work_orders = WorkOrder.objects.filter(
            assigned_to=user
        ).exclude(
            status='COMPLETED'
        ).order_by('-created_at')[:5]
        
        if not work_orders:
            message = """
📋 <b>Mis Órdenes de Trabajo</b>

No tienes órdenes de trabajo asignadas.
"""
        else:
            message = "📋 <b>Mis Órdenes de Trabajo</b>\n\n"
            
            for wo in work_orders:
                status_emoji = {
                    'PENDING': '⏳',
                    'IN_PROGRESS': '🔧',
                    'ON_HOLD': '⏸️'
                }.get(wo.status, '📋')
                
                priority_emoji = {
                    'LOW': '🔵',
                    'MEDIUM': '🟡',
                    'HIGH': '🟠',
                    'CRITICAL': '🔴'
                }.get(wo.priority, '⚪')
                
                message += f"{status_emoji} <b>{wo.work_order_number}</b>\n"
                message += f"   {priority_emoji} {wo.get_priority_display()}\n"
                message += f"   📦 {wo.asset.name if wo.asset else 'Sin activo'}\n"
                message += f"   📅 {wo.created_at.strftime('%d/%m/%Y')}\n\n"
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in /ordenes: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al obtener tus órdenes de trabajo."
        )


@require_linked_user
def handle_pendientes(chat_id, user_info, telegram_service, user):
    """Handle /pendientes command - Pending work orders count"""
    from apps.work_orders.models import WorkOrder
    
    try:
        pending_count = WorkOrder.objects.filter(
            assigned_to=user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).count()
        
        in_progress = WorkOrder.objects.filter(
            assigned_to=user,
            status='IN_PROGRESS'
        ).count()
        
        pending = WorkOrder.objects.filter(
            assigned_to=user,
            status='PENDING'
        ).count()
        
        message = f"""
📊 <b>Órdenes Pendientes</b>

<b>Total:</b> {pending_count}

🔧 En Progreso: {in_progress}
⏳ Pendientes: {pending}

💡 Usa /ordenes para ver el detalle.
"""
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in /pendientes: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al obtener órdenes pendientes."
        )


@require_linked_user
def handle_alertas(chat_id, user_info, telegram_service, user):
    """Handle /alertas command - Recent alerts"""
    from apps.notifications.models import Notification
    
    try:
        alerts = Notification.objects.filter(
            user=user,
            priority__in=['HIGH', 'CRITICAL']
        ).order_by('-created_at')[:5]
        
        if not alerts:
            message = """
🚨 <b>Alertas Recientes</b>

No tienes alertas de alta prioridad.
"""
        else:
            message = "🚨 <b>Alertas Recientes</b>\n\n"
            
            for alert in alerts:
                priority_emoji = {
                    'HIGH': '🟠',
                    'CRITICAL': '🔴'
                }.get(alert.priority, '⚪')
                
                read_status = '✓' if alert.is_read else '●'
                
                message += f"{priority_emoji} {read_status} <b>{alert.title}</b>\n"
                message += f"   {alert.message[:50]}...\n"
                message += f"   📅 {alert.created_at.strftime('%d/%m %H:%M')}\n\n"
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in /alertas: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al obtener alertas."
        )


@require_linked_user
@require_role(['ADMIN', 'MANAGER'])
def handle_kpis(chat_id, user_info, telegram_service, user):
    """Handle /kpis command - Key metrics"""
    from apps.work_orders.models import WorkOrder
    from apps.assets.models import Asset
    from apps.predictions.models import FailurePrediction
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    try:
        # Work Orders stats
        total_wo = WorkOrder.objects.count()
        pending_wo = WorkOrder.objects.filter(status='PENDING').count()
        in_progress_wo = WorkOrder.objects.filter(status='IN_PROGRESS').count()
        completed_wo = WorkOrder.objects.filter(status='COMPLETED').count()
        
        # Assets stats
        total_assets = Asset.objects.filter(status='ACTIVE').count()
        
        # Predictions stats
        high_risk = FailurePrediction.objects.filter(
            risk_level__in=['HIGH', 'CRITICAL']
        ).count()
        
        # Recent completion rate
        last_30_days = datetime.now() - timedelta(days=30)
        recent_wo = WorkOrder.objects.filter(created_at__gte=last_30_days)
        recent_completed = recent_wo.filter(status='COMPLETED').count()
        completion_rate = (recent_completed / recent_wo.count() * 100) if recent_wo.count() > 0 else 0
        
        message = f"""
📊 <b>KPIs del Sistema</b>

<b>📋 Órdenes de Trabajo:</b>
Total: {total_wo}
⏳ Pendientes: {pending_wo}
🔧 En Progreso: {in_progress_wo}
✅ Completadas: {completed_wo}

<b>📦 Activos:</b>
Activos: {total_assets}

<b>🔮 Predicciones:</b>
⚠️ Alto Riesgo: {high_risk}

<b>📈 Últimos 30 días:</b>
Tasa de Completitud: {completion_rate:.1f}%

<i>Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>
"""
        
        telegram_service.send_message(
            chat_id=str(chat_id),
            text=message.strip(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in /kpis: {str(e)}")
        telegram_service.send_message(
            chat_id=str(chat_id),
            text="❌ Error al obtener KPIs."
        )
