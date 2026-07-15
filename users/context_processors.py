from .models import Usuario, Empleado, Tarea, TransferRequest
from configuracion.models import Rol_permiso
from configuracion.views import obtener_permisos

def notificaciones_empleado(request):
    """
    Procesador de contexto para obtener alertas y notificaciones 
    pendientes del empleado logueado para mostrar en el badge del menú.
    """
    if not request.user.is_authenticated:
        return {}

    usuario_id = request.session.get('usuario_logeado')
    
    # Búsqueda robusta del usuario
    usuario_profile = Usuario.objects.filter(id=usuario_id).first()
    if not usuario_profile:
        usuario_profile = Usuario.objects.filter(user_id=request.user).first()

    if not usuario_profile:
        return {'notificaciones_conteo': 0, 'notificaciones_inventario': 0}

    # Conteo de tareas operativas pendientes asignadas al empleado
    conteo_tareas = Tarea.objects.filter(empleado_id=usuario_profile.id, completada=False).count()
    
    # Conteo de solicitudes de inventario pendientes (Solo para Administradores)
    conteo_inventario = 0
    empleado = Empleado.objects.filter(id=usuario_profile.id).first()
    if request.user.is_superuser or (empleado and empleado.id_rol and empleado.id_rol.nombre.strip().upper() == "ADMINISTRADOR"):
        conteo_inventario = TransferRequest.objects.filter(status='PENDING').count()

    return {
        'notificaciones_conteo': conteo_tareas,
        'notificaciones_inventario': conteo_inventario
    }

def menu_data(request):
    """
    Procesador de contexto para asegurar que los datos del perfil y 
    permisos del menú estén disponibles en todas las vistas del dashboard.
    """
    if not request.user.is_authenticated:
        return {}

    usuario_id = request.session.get('usuario_logeado')

    # Búsqueda robusta del perfil de usuario
    usuario_profile = Usuario.objects.filter(id=usuario_id).first()
    if not usuario_profile:
        usuario_profile = Usuario.objects.filter(user_id=request.user).first()

    if not usuario_profile and not request.user.is_superuser:
        return {}

    try:
        empleado_profile = Empleado.objects.filter(id=usuario_profile.id).first() if usuario_profile else None
        
        permisos = {}
        nombre_rol = "USUARIO" # Default normalized role
        if request.user.is_superuser:
            # Otorgar todos los permisos al superusuario de forma predeterminada
            permisos = {'crear': 1, 'consultar': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1, 'inventario': 1}
            nombre_rol = "ADMINISTRADOR"
        elif empleado_profile and empleado_profile.id_rol:
            nombre_rol = empleado_profile.id_rol.nombre.strip().upper() # Normalize once
            permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
            permisos = obtener_permisos(permisos_qs)
            if nombre_rol == "ADMINISTRADOR":
                permisos = {
                    'crear': 1, 'consultar': 1, 'editar': 1,
                    'eliminar': 1, 'usuarios': 1, 'inventario': 1
                }

        # Determinar la URL del Dashboard principal según el rol para el menú
        if request.user.is_superuser or nombre_rol.startswith("ADMINISTRADOR"):
            dashboard_home = 'perfil_admin'
        else:
            dashboard_home = 'perfil_empleado'

        # Banderas de visibilidad lógica
        # Banderas de visibilidad lógica (Cálculo robusto y unificado)
        is_admin = nombre_rol.startswith("ADMINISTRADOR") or request.user.is_superuser
        is_supervisor = nombre_rol.startswith("SUPERVISOR") or request.user.is_superuser
        has_profile = empleado_profile is not None

        return {
            'usuario_global': usuario_profile,
            'nombre_rol_global': nombre_rol, # Use the normalized role
            # Banderas de Visibilidad del Menú (Set COMPLETO para evitar cambios)
            'menu_inicio_visible': True,
            'menu_dashboard_visible': is_admin or is_supervisor,
            'menu_usuarios_visible': is_admin,
            'menu_empleados_visible': is_admin,
            'menu_roles_visible': is_admin,
            'menu_inventario_visible': is_admin or is_supervisor or (permisos and permisos.get('inventario', 0) == 1),
            'menu_tareas_visible': is_admin or is_supervisor,
            'menu_cursos_visible': is_admin,
            'menu_publicaciones_visible': is_admin,
            'menu_auditoria_visible': is_admin,
            'menu_rrhh_visible': is_admin,
            'menu_pqrs_visible': is_admin,
            'menu_cotizaciones_visible': is_admin,
            'menu_nosotros_visible': is_admin,
            'menu_agenda_visible': has_profile, 
            'menu_perfil_visible': True,
            # Nombres estandarizados para coincidir con las vistas y evitar que el menú desaparezca
            'usuario': usuario_profile,
            'nombre_rol': nombre_rol, # Use the normalized role
            'usuarios': is_admin or (permisos and permisos.get('usuarios', 0) == 1),
            'inventario': 1 if (permisos and permisos.get('inventario', 0) == 1 or is_admin or is_supervisor) else 0,
            'crear': permisos and permisos.get('crear', 0) == 1,
            'consultar': permisos and permisos.get('consultar', 0) == 1,
            'editar': permisos and permisos.get('editar', 0) == 1,
            'eliminar': permisos and permisos.get('eliminar', 0) == 1,
            'is_supervisor': is_supervisor,
            'is_admin': is_admin,
            'dashboard_home': dashboard_home,
        }
    except Exception:
        return {}