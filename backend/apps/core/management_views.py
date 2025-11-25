"""
Management views for administrative tasks
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from io import StringIO


@csrf_exempt
@require_http_methods(["POST"])
def populate_database(request):
    """
    Execute the populate_db management command
    Requires admin authentication
    """
    try:
        # Capture command output
        out = StringIO()
        err = StringIO()
        
        # Execute the management command
        call_command('populate_db', stdout=out, stderr=err)
        
        return JsonResponse({
            'success': True,
            'stdout': out.getvalue(),
            'stderr': err.getvalue()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'stdout': out.getvalue() if 'out' in locals() else '',
            'stderr': err.getvalue() if 'err' in locals() else ''
        }, status=500)
