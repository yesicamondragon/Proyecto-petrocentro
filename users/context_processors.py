from .models import Empleado, Tarea, EmpleadoCurso
from paginaPetrocentro.models import Usuario
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def notificaciones_empleado(request):
    """
    Calcula notificaciones globales para el empleado:
    1. Tareas vencidas o por vencer (3 días).
    2. Cursos pendientes, rechazados o próximos a vencer.
    """
    if not request.user.is_authenticated:
        return {}

    try:
        # Obtener el perfil de empleado a partir del usuario logueado
        usuario = Usuario.objects.get(user_id=request.user)
        empleado = Empleado.objects.get(id=usuario.id)
    except (Usuario.DoesNotExist, Empleado.DoesNotExist):
        return {}

    today = timezone.now().date()
    limit_task = today + timedelta(days=3) # Tareas que vencen en 3 días
    limit_cert = today + timedelta(days=30) # Certificados que vencen en 30 días

    # Tareas: Pendientes que están vencidas o vencen pronto
    tareas_count = Tarea.objects.filter(
        empleado=empleado,
        completada=False
    ).filter(
        Q(fecha_limite__lt=today) | Q(fecha_limite__lte=limit_task)
    ).count()

    # Cursos: Pendientes, Rechazados O Aprobados pero por vencer
    cursos_count = EmpleadoCurso.objects.filter(
        empleado=empleado
    ).filter(
        Q(estado__in=['PENDIENTE', 'RECHAZADO']) | 
        (Q(estado='APROBADO') & Q(fecha_vencimiento__lte=limit_cert) & Q(fecha_vencimiento__gte=today))
    ).count()

    return {
        'total_notificaciones': tareas_count + cursos_count
    }