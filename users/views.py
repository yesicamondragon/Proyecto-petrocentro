from django.shortcuts import redirect, render
from django.contrib.sessions.models import Session
from django.http import HttpResponse, JsonResponse
import openpyxl
import json
from paginaPetrocentro.models import *
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.db.models import Q, Count, Case, When, IntegerField
from paginaPetrocentro.forms import RegisterForm
from configuracion.models import *
from configuracion.views import obtener_permisos
from django.utils import timezone
from openpyxl.styles import Font, Alignment
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa

# --- UTILIDADES ---
def obtener_contexto_usuario(request):
    """
    Centraliza la obtención del perfil de usuario, empleado y permisos
    para evitar repetición de código en las vistas.
    """
    usuario_id = request.session.get('usuario_logeado')
    user = request.user
    
    permisos = {}
    usuario_profile = get_object_or_404(Usuario, id=usuario_id)
    empleado_profile = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'consultar': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        empleado_profile = Empleado.objects.filter(id=usuario_profile.id).first()
    else:
        try:
            empleado_profile = Empleado.objects.get(id=usuario_profile.id)
            if empleado_profile.id_rol:
                nombre_rol = empleado_profile.id_rol.nombre
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            pass
            
    return {
        'usuario': usuario_profile,
        'empleado': empleado_profile,
        'permisos': permisos,
        'nombre_rol': nombre_rol
    }

#------------------------------------------------------EMPLEADOS Y USUARIOS----------------------------------------------
@login_required
def listar_empleados(request):
    ctx = obtener_contexto_usuario(request)
    if not ctx['empleado'] and not request.user.is_superuser:
        messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
        return redirect('index')

    permisos = ctx['permisos']
 
    # LÓGICA DE ACCESO:
    # Si tiene permiso 'usuarios' (Admin/Gestor), ve todos los empleados y puede registrar nuevos.
    if permisos.get('usuarios') == 1:
            lista_empleados = Empleado.objects.select_related('user_id', 'id_rol', 'id_cargo', 'id_ubicacion').all()
            users_para_registro = Usuario.objects.all()
    else:
            # Si es empleado regular, entra a la ruta pero SOLO ve su propia información.
            lista_empleados = Empleado.objects.select_related('user_id', 'id_rol', 'id_cargo', 'id_ubicacion').filter(id=ctx['usuario'].id)
            users_para_registro = Usuario.objects.none() # No puede registrar a otros
        
    #----------------------------------------------------------------------------------------------------------------
    # FILTROS
    busqueda = request.GET.get("buscar") 
    fecha = request.GET.get("fechaI")
    estado= request.GET.get("estado")
    filtro_cargo = request.GET.get("cargo")
    filtro_ubicacion = request.GET.get("ubicacion")
 
    if estado and estado != "0":
        lista_empleados = lista_empleados.filter(Q(estado = estado)).distinct()
        
    if busqueda:
        lista_empleados = lista_empleados.filter(
            Q(id__icontains = busqueda)|
            Q(nombre__icontains = busqueda)|
            Q(telefono__icontains= busqueda)|
            Q(identificacion__icontains= busqueda)|
            Q(correo__icontains = busqueda)|
            Q(id_rol__nombre__icontains = busqueda)|
            Q(id_cargo__nombre__icontains = busqueda)|
            Q(id_ubicacion__nombre__icontains = busqueda)
        )
 
    if fecha: 
        lista_empleados = lista_empleados.filter(Q(fecha_ingreso__icontains = fecha)).distinct()
 
    if filtro_cargo and filtro_cargo != '0':
        lista_empleados = lista_empleados.filter(id_cargo_id=filtro_cargo)
    
    if filtro_ubicacion and filtro_ubicacion != '0':
        lista_empleados = lista_empleados.filter(id_ubicacion_id=filtro_ubicacion)

    #----------------------------------------------------------------------------------------------------------------   

    # Optimizamos la consulta con anotaciones para evitar consultas dentro del bucle
    lista_empleados = lista_empleados.annotate(
        total_cursos_count=Count('cursos_asignados', distinct=True),
        aprobados_count=Count('cursos_asignados', filter=Q(cursos_asignados__estado='APROBADO'), distinct=True),
        total_tareas_count=Count('tarea', distinct=True),
        completadas_count=Count('tarea', filter=Q(tarea__completada=True), distinct=True)
    )

    p = Paginator(lista_empleados, 5)
    page_number = request.GET.get('page')
    pagina= p.get_page(page_number)

    # Calcular nivel de cumplimiento para los empleados mostrados
    for emp in pagina:
        emp.cumplimiento = int((emp.aprobados_count / emp.total_cursos_count) * 100) if emp.total_cursos_count > 0 else 0
        emp.cumplimiento_tareas = int((emp.completadas_count / emp.total_tareas_count) * 100) if emp.total_tareas_count > 0 else 0

        
    data ={
        'cargos': Cargo.objects.all(),
        'cursos': Curso.objects.all(), # Para el modal de asignar curso
        'ubicaciones': Ubicacion.objects.all(),
        'roles': Rol.objects.all(),
        'users': users_para_registro, # Lista de usuarios para el modal de registro                  
        'paginas': pagina,
        'paginator': p,
        'nombre_rol': ctx['nombre_rol'],
        'usuario': ctx['usuario'],
        'empleado': ctx['empleado'],
        'crear':permisos.get('crear', 0),
        'consultar': permisos.get('consultar', 0),
        'editar': permisos.get('editar', 0),
        'eliminar': permisos.get('eliminar', 0),
        'usuarios': permisos.get('usuarios', 0),
        'filtros': {'buscar': busqueda, 'estado': estado, 'cargo': filtro_cargo, 'ubicacion': filtro_ubicacion, 'fecha': fecha}
        }
        
    return render(request,'dash/empleados.html',data)

    #Obtener todos las tablas de la base de datos

@login_required
def editar_empleados(request, id):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user
 
    # --- Verificación de permisos para EDITAR ---
    permisos = {}
    if user.is_superuser:
        permisos['editar'] = 1
    else:
        try:
            empleado_logeado = Empleado.objects.get(id=usuario_logeado_id)
            if empleado_logeado.id_rol:
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_logeado.id_rol)
                permisos = obtener_permisos(permisos_qs)
        except (Usuario.DoesNotExist, Empleado.DoesNotExist):
            pass
 
    if not permisos.get('editar') == 1:
        messages.error(request, 'No tienes permisos para editar empleados.')
        return redirect('empleados')

    if request.method == 'POST':
        #consulta para obtener el empleado que coincida con el id que envia el botón de editar
        usuario = Empleado.objects.get(id=id)
        

        #----------------------------------------------------------------------------------------------------------------
        try:    
            #Variable para almacenar el cargo enviado en el formulario, ya que solo se permite editar el cargo
            id_cargo = request.POST.get('cargo')
        
            id_rol = request.POST.get('rol')
            telefono = request.POST.get('telefono1')
            identificacion = request.POST.get('identificacion1')
            #En la variable usuario, se obtiene el cargo y se realiza una consulta que trae el cargo de la tabla "CARGO" para validar coincidencias y asi mismo cambiarlo en el empleado
            usuario.telefono = telefono
            usuario.identificacion = identificacion
           
            usuario.id_cargo = Cargo.objects.get(id_cargo = id_cargo)
        
            if id_rol != '#':
                usuario.id_rol = Rol.objects.get(id_rol = id_rol)
            else:
                usuario.id_rol = None
            #gurdar el cargo
            usuario.save()
            
            # --- LOG DE ACTIVIDAD ---
            try:
                admin_resp = Usuario.objects.get(id=usuario_logeado_id)
                LogActividad.objects.create(
                    usuario_afectado=usuario, # Empleado hereda de Usuario
                    admin_responsable=admin_resp,
                    accion="Edición de Empleado",
                    detalles=f"Se actualizaron datos (Cargo/Rol/Teléfono) de {usuario.nombre}"
                )
            except:
                pass
            
            #si es exitoso el cambio, envía un mensaje de éxito.
            if(usuario):
                messages.success(request, f'Empleado {usuario.nombre} actualizado correctamente.')
            
          
            #si no es exitoso, envía un mensaje de error
            else:
                messages.error(request, 'No se ha editado exitosamente')
                
        #excepciones para validar errores
        except (KeyError, ValueError) as e:
            messages.error(request, e)
            
    return redirect('empleados')

@login_required
def registrar_empleados(request):

    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Verificación de permisos para CREAR ---
    permisos = {}
    if user.is_superuser:
        permisos['crear'] = 1
    else:
        try:
            empleado_logeado = Empleado.objects.get(id=usuario_logeado_id)
            if empleado_logeado.id_rol:
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_logeado.id_rol)
                permisos = obtener_permisos(permisos_qs)
        except (Usuario.DoesNotExist, Empleado.DoesNotExist):
            pass

    if not permisos.get('crear') == 1:
        messages.error(request, 'No tienes permisos para registrar empleados.')
        return redirect('empleados')

    if request.method == 'POST':
        
        #----------------------------------------------------------------------------------------------------------------
        #try para pedirle que en caso que falle, arroje el error en un mensaje y no el error de django 

            #Obtener toda la informacion del dormulario de empleados
            fecha = request.POST.get("fechaIngreso")
            id_cargo = request.POST.get('cargo')
            id_rol= request.POST.get('rol')
            identificacion = request.POST.get('identificacion')
            telefono = request.POST.get('telefono')
            ubicacion = request.POST.get('ubicacion')
            usuario_id= request.POST.get('usuario_id')
            
            
            #----------------------------------------------------------------------------------------------------------------
            #Obtener las fechas y convertirlas 
            fechaH = datetime.strptime(fecha, '%Y-%m-%d').date()
        
            #Obtener fecha de hoy 
            fecha_hoy= datetime.today().date()
            
            #----------------------------------------------------------------------------------------------------------------
            #Obtener el id_user que tiene el usuario
            user = Usuario.objects.get(id = usuario_id)
            usuario_num = user.user_id.pk

            #----------------------------------------------------------------------------------------------------------------

            if not id_rol or id_rol == "#":
            #instancia de empleado para crear el mismo
                empleado= Empleado(
                
                        id=user.id,  # Usar la clave primaria del usuario
                        user_id= User.objects.get(id=usuario_num),  #la clave de user_auth para el usuario
                        identificacion= identificacion,
                        estado=user.estado,
                        nombre=user.nombre,
                        correo=user.correo,
                        telefono=telefono,
                        fecha_ingreso=fecha,
                        
                        id_cargo= Cargo.objects.get(id_cargo = id_cargo),
                        
  
                        id_ubicacion=Ubicacion.objects.get(idUbicacion = ubicacion),

                        )
                
            else:
                        empleado= Empleado(
                
                        id=user.id,  # Usar la clave primaria del usuario
                        user_id= User.objects.get(id=usuario_num),  #la clave de user_auth para el usuario
                        identificacion= identificacion,
                        estado=user.estado,
                        nombre=user.nombre,
                        correo=user.correo,
                        telefono=telefono,
                        fecha_ingreso=fecha,
                        id_rol = Rol.objects.get(id_rol = id_rol ),
                        id_cargo= Cargo.objects.get(id_cargo = id_cargo),
                    
                        id_ubicacion=Ubicacion.objects.get(idUbicacion = ubicacion),

                        )
            #----------------------------------------------------------------------------------------------------------------
            #Condición para valdiar si el empleado ya existe
            if (Empleado.objects.filter(id=usuario_id)).exists():
                messages.error(request, 'No se ha registrado exitosamente, el empleado ya existe.')
            
            #----------------------------------------------------------------------------------------------------------------            
            #condicion para validar que el empleado no se puede registrar un dia mayor al actual
            elif(fechaH > fecha_hoy):
                messages.error(request, 'No se puede registrar una fecha superior al dia presente.')
            
            #----------------------------------------------------------------------------------------------------------------            
            #si todo lo anterior se cumple, guarde el empleado
            else:
                empleado.save()
                messages.success(request, f'Empleado {empleado.nombre} registrado exitosamente.')
                

    return redirect('empleados')

#funcion para cambiar el estado de un empleado
@login_required  
def cambiar_estado(request, id):
    # Obtener el objeto Usuario completo
    usuario = get_object_or_404(Usuario, id=id)

    #----------------------------------------------------------------------------------------------------------------
    #obtener solo el estado del usuario
    id_estado1 = usuario.estado.id
    
    #comparar si el estado del usuario es uigual a dos
    #----------------------------------------------------------------------------------------------------------------
    if id_estado1 == 2:

      
        #generar una variable que es la que cambiara el estado 
        id_estado = 1
        
        #cambiar el estado de Id_estado con el registrado
        # Usamos get_or_create para asegurar que el estado exista. Si no, lo crea.
        estado, _ = Estado.objects.get_or_create(id=id_estado, defaults={'nombre': 'Activo'})
        
        #se agrega a el campo de estado en la base de datos 
        usuario.estado = estado
        
        #se guarda el estado del usuario en la base de datos
        usuario.save()
        
        if usuario:
            messages.success(request, f'Estado de {usuario.nombre} activado correctamente.')
        else:
            messages.error(request, 'No se ha cambiado el estado correctamente')
   
    #----------------------------------------------------------------------------------------------------------------
    else:
        user = usuario.user_id # Accedemos directamente al objeto User relacionado

# Cierra la sesión de usuarios cuya cuenta está deshabilitada
        if user.is_active:
            # Buscar las sesiones activas del usuario
            active_sessions =  Session.objects.filter(expire_date__gte=timezone.now())


            for session in active_sessions:
              # Si hay más de una sesión activa, se desloguea la última
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(user.id):
                    messages.error(request,'cuenta deshabilitada')
                    # Eliminar la sesión activa
                    session.delete()
                 
             
              
        #generar una variable que es la que cambiara el estado        
        id_estado = 2
        
        #cambiar el estado de Id_estado con el registrado      
        # Usamos get_or_create para asegurar que el estado exista. Si no, lo crea.
        estado, _ = Estado.objects.get_or_create(id=id_estado, defaults={'nombre': 'Inactivo'})
        
        #se agrega a el campo de estado en la base de datos 
        usuario.estado = estado      
        #se guarda el estado del usuario en la base de datos 
        usuario.save()
        if usuario:
            messages.success(request, f'Estado de {usuario.nombre} desactivado correctamente.')
        else:
            messages.error(request, 'No se ha cambiado el estado correctamente')

    return redirect('empleados')

@login_required
def registrar_usuario(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'consultar': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado = Empleado.objects.get(id=emp.id)
        except Empleado.DoesNotExist:
            pass # Superuser might not be an employee
    else:
        try:
            empleado = Empleado.objects.get(id=emp.id)
            if empleado.id_rol:
                rol_nom = empleado.id_rol.nombre
                nombre_rol = rol_nom
                permiso_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permiso_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # Ahora, se verifica si el usuario tiene el permiso 'usuarios'
    if permisos.get('usuarios') == 1:
        # Lógica de la vista (GET)
        user_list = Usuario.objects.select_related('user_id', 'estado', 'empleado', 'empleado__id_cargo', 'empleado__id_rol').all().order_by('-user_id__date_joined')
        
        # --- FILTROS AVANZADOS ---
        busqueda = request.GET.get('buscar')
        filtro_estado = request.GET.get('estado')
        filtro_cargo = request.GET.get('cargo')
        filtro_fecha = request.GET.get('fecha')

        if busqueda:
            user_list = Usuario.objects.filter(
                Q(nombre__icontains=busqueda) |
                Q(correo__icontains=busqueda) |
                Q(empleado__id_cargo__nombre__icontains=busqueda)
            ).distinct()

        if filtro_estado and filtro_estado != '0':
            user_list = user_list.filter(estado_id=filtro_estado)
        
        if filtro_cargo and filtro_cargo != '0':
            user_list = user_list.filter(empleado__id_cargo_id=filtro_cargo)
            
        if filtro_fecha:
            user_list = user_list.filter(user_id__date_joined__date=filtro_fecha)

        form = RegisterForm(request.POST or None)
        p = Paginator(user_list, 10) # 10 por página
        page_number = request.GET.get('page')
        pagina = p.get_page(page_number)

        # Lógica de la vista (POST)
        if request.method == 'POST' and form.is_valid():
            username = form.cleaned_data.get('username')
            # ... validaciones de contraseña existentes en el form o aquí ...
            if form.cleaned_data.get('contraseña') != form.cleaned_data.get('confirmar_contraseña'):
                 messages.error(request, 'Las contraseñas no coinciden.')
            elif User.objects.filter(username=username).exists():
                 messages.error(request, 'El usuario ya existe.')
            else:
                 new_user = form.save()
                 usuario_creado = Usuario.objects.create(
                     user_id=new_user,
                     estado=Estado.objects.get(id=1),
                     nombre=form.cleaned_data['Nombre_completo'],
                     correo=form.cleaned_data['correo_electronico'],
                 )
                 
                 # Log de auditoría
                 try:
                     admin_resp = Usuario.objects.get(id=usuario_logeado_id)
                     LogActividad.objects.create(
                         usuario_afectado=usuario_creado,
                         admin_responsable=admin_resp,
                         accion="Creación de Usuario",
                         detalles=f"Usuario registrado manualmente por {admin_resp.nombre}"
                     )
                 except:
                     pass
                     
                 messages.success(request, 'Registro Exitoso.')
                 return redirect('usuarios')

        data = {
            'form': form,
            'paginas': pagina,
            'paginator': p,
            'usuario': emp,
            'empleado': empleado,
            'nombre_rol': nombre_rol,
            'crear': permisos.get('crear', 0),
            'consultar': permisos.get('consultar', 0),
            'editar': permisos.get('editar', 0),
            'eliminar': permisos.get('eliminar', 0),
            'usuarios': permisos.get('usuarios', 0),
            # Datos para filtros y modales
            'cargos': Cargo.objects.all(),
            'roles': Rol.objects.all(),
            'filtros': {
                'estado': filtro_estado,
                'cargo': filtro_cargo,
                'fecha': filtro_fecha,
                'buscar': busqueda
            }
        }
        return render(request, 'dash/usuarios.html', data)
    
    # Caso 3: El usuario no tiene el permiso 'usuarios'.
    else:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('index')

@login_required
def cambiar_estado_usuario(request, id):
    # Versión específica para la vista de usuarios
    if not request.user.is_superuser:
        messages.error(request, "Acción no autorizada.")
        return redirect('usuarios')

    usuario = get_object_or_404(Usuario, id=id)
    nuevo_estado_id = 2 if usuario.estado.id == 1 else 1
    nuevo_estado_nombre = "Inactivo" if nuevo_estado_id == 2 else "Activo"
    
    estado_obj, _ = Estado.objects.get_or_create(id=nuevo_estado_id, defaults={'nombre': nuevo_estado_nombre})
    usuario.estado = estado_obj
    usuario.save()

    # Si se desactiva, cerrar sesiones activas (User de Django)
    if nuevo_estado_id == 2:
        usuario.user_id.is_active = False
    else:
        usuario.user_id.is_active = True
    usuario.user_id.save()

    # Log
    try:
        admin_resp = Usuario.objects.get(id=request.session.get('usuario_logeado'))
        LogActividad.objects.create(
            usuario_afectado=usuario,
            admin_responsable=admin_resp,
            accion="Cambio de Estado",
            detalles=f"Estado cambiado a {nuevo_estado_nombre}"
        )
    except:
        pass

    messages.success(request, f"Estado de {usuario.nombre} actualizado a {nuevo_estado_nombre}.")
    return redirect('usuarios')

@login_required
def editar_usuario_rapido(request, id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id)
        rol_id = request.POST.get('rol')
        cargo_id = request.POST.get('cargo')

        # Gestionar perfil de Empleado
        empleado, created = Empleado.objects.get_or_create(id=usuario.id, defaults={
            'user_id': usuario.user_id,
            'identificacion': 0, 'telefono': '0',
            'fecha_ingreso': timezone.now().date(),
            'id_ubicacion': Ubicacion.objects.first(), # Default fallback
            'id_cargo': Cargo.objects.first(), # Default fallback
            'estado': usuario.estado,
            'nombre': usuario.nombre, 'correo': usuario.correo
        })

        if rol_id:
            empleado.id_rol_id = rol_id
        if cargo_id:
            empleado.id_cargo_id = cargo_id
        
        empleado.save()
        
        # Log
        try:
            admin_resp = Usuario.objects.get(id=request.session.get('usuario_logeado'))
            LogActividad.objects.create(
                usuario_afectado=usuario,
                admin_responsable=admin_resp,
                accion="Edición Rápida",
                detalles=f"Actualización de Rol/Cargo"
            )
        except:
            pass

        messages.success(request, "Usuario actualizado correctamente.")
    return redirect('usuarios')

@login_required
def reset_password_usuario(request, id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id)
        new_pass = request.POST.get('new_password')
        
        if new_pass:
            user_django = usuario.user_id
            user_django.set_password(new_pass)
            user_django.save()
            
            # Log
            try:
                admin_resp = Usuario.objects.get(id=request.session.get('usuario_logeado'))
                LogActividad.objects.create(
                    usuario_afectado=usuario,
                    admin_responsable=admin_resp,
                    accion="Reset Contraseña",
                    detalles="Contraseña restablecida desde panel admin"
                )
            except:
                pass

            messages.success(request, f"Contraseña actualizada para {usuario.nombre}.")
    return redirect('usuarios')

@login_required
def exportar_usuarios_excel(request):
    # Reutilizar lógica de filtros del listado principal
    busqueda = request.GET.get('buscar')
    filtro_estado = request.GET.get('estado')
    filtro_cargo = request.GET.get('cargo')
    filtro_fecha = request.GET.get('fecha')

    user_list = Usuario.objects.select_related('empleado', 'empleado__id_cargo', 'empleado__id_rol').all()

    if busqueda:
        user_list = user_list.filter(Q(nombre__icontains=busqueda) | Q(correo__icontains=busqueda)).distinct()
    if filtro_estado and filtro_estado != '0':
        user_list = user_list.filter(estado_id=filtro_estado)
    if filtro_cargo and filtro_cargo != '0':
        user_list = user_list.filter(empleado__id_cargo_id=filtro_cargo)
    if filtro_fecha:
        user_list = user_list.filter(user_id__date_joined__date=filtro_fecha)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Reporte Usuarios'

    headers = ['ID', 'Nombre', 'Correo', 'Estado', 'Cargo', 'Rol', 'Fecha Registro']
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for u in user_list:
        cargo = u.empleado.id_cargo.nombre if hasattr(u, 'empleado') and u.empleado and u.empleado.id_cargo else 'N/A'
        rol_nombre = u.empleado.id_rol.nombre if hasattr(u, 'empleado') and u.empleado and u.empleado.id_rol else 'N/A'
        estado = u.estado.nombre if u.estado else 'Desconocido'
        fecha = u.user_id.date_joined.strftime('%Y-%m-%d') if u.user_id.date_joined else 'N/A'

        rol = rol_nombre
        
        sheet.append([u.id, u.nombre, u.correo, estado, cargo, rol, fecha])

    for col in ['B', 'C', 'E', 'F']: sheet.column_dimensions[col].autosize = True

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="usuarios_filtrados.xlsx"'
    workbook.save(response)
    return response

# -------------------------------- GESTIÓN DE TAREAS (Lógica Cargo/Rol) --------------------------------

@login_required
def gestion_tareas(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado_profile = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado_profile = Empleado.objects.get(id=usuario_profile.id)
        except Empleado.DoesNotExist:
            pass # Superuser might not be an employee
    else:
        try:
            empleado_profile = Empleado.objects.get(id=usuario_profile.id)
            if empleado_profile.id_rol:
                rol_nom = empleado_profile.id_rol.nombre
                nombre_rol = rol_nom
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # 2. Filtrar Tareas según CARGO (Tareas Concretas)
    if nombre_rol == "Administrador":
        # El administrador (Rol) tiene acceso global, ve todas las tareas de todos los cargos
        tareas = Tarea.objects.select_related('empleado', 'id_cargo').all()
        
        # Filtros para el admin
        empleado_filtro = request.GET.get('empleado_filtro')
        estado_filtro = request.GET.get('estado_tarea')

        if empleado_filtro:
            tareas = tareas.filter(empleado__id=empleado_filtro)
        
        if estado_filtro == 'completada':
            tareas = tareas.filter(completada=True)
        elif estado_filtro == 'pendiente':
            tareas = tareas.filter(completada=False)

        tareas = tareas.order_by('-fecha_creacion')
        lista_completa_empleados = Empleado.objects.all().order_by('nombre')
    else:
        # El empleado ve SOLO las tareas asignadas a su CARGO específico
        if empleado_profile and empleado_profile.id_cargo:
            tareas = Tarea.objects.filter(empleado=empleado_profile).order_by('fecha_limite')
        else:
            tareas = Tarea.objects.none()
        lista_completa_empleados = Empleado.objects.none()

    # Determinar si el usuario tiene permiso para crear tareas
    is_manager_cargo = False
    if empleado_profile and empleado_profile.id_cargo:
        is_manager_cargo = empleado_profile.id_cargo.nombre in [
            "Gerente de Operaciones", 
            "Administrador de Contrato", 
            "Coordinador de Operaciones",
            "Coordinador HSEQ"
        ]
    can_create_tasks = permisos.get('crear') == 1 and (user.is_superuser or is_manager_cargo)

    # 3. Lógica para Crear Tarea (Solo si tiene permiso por Rol y Cargo)
    if request.method == 'POST':
        if can_create_tasks:
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            fecha_limite = request.POST.get('fecha_limite')
            id_cargo_destino = request.POST.get('id_cargo')
            id_empleado_destino = request.POST.get('id_empleado')
            
            if id_empleado_destino:
                # Opción A: Asignar a un empleado específico
                try:
                    emp = Empleado.objects.get(id=id_empleado_destino)
                    Tarea.objects.create(
                        titulo=titulo,
                        descripcion=descripcion,
                        fecha_limite=fecha_limite,
                        id_cargo=emp.id_cargo, 
                        empleado=emp
                    )
                    # Notificación por correo
                    try:
                        send_mail(
                            'Nueva Tarea Asignada - Petrocentro',
                            f'Hola {emp.nombre},\n\nSe te ha asignado una nueva tarea: "{titulo}".\nFecha límite: {fecha_limite}\n\nDescripción: {descripcion}\n\nPor favor ingresa a tu agenda para gestionarla.',
                            settings.EMAIL_HOST_USER,
                            [emp.correo],
                            fail_silently=True
                        )
                    except:
                        pass
                    messages.success(request, f'Tarea asignada correctamente a {emp.nombre}.')
                except Empleado.DoesNotExist:
                    messages.error(request, 'El empleado seleccionado no existe.')
                    
            elif id_cargo_destino:
                # Opción B: Asignar masivamente por cargo
                cargo = Cargo.objects.get(id_cargo=id_cargo_destino)
                empleados = Empleado.objects.filter(id_cargo=cargo)
                
                # Creamos una tarea individual para CADA empleado del cargo
                count = 0
                for emp in empleados:
                    Tarea.objects.create(
                        titulo=titulo,
                        descripcion=descripcion,
                        fecha_limite=fecha_limite,
                        id_cargo=cargo,
                        empleado=emp # Asignación individual
                    )
                    # Notificación por correo (individual en bucle)
                    try:
                        send_mail(
                            'Nueva Tarea Asignada - Petrocentro',
                            f'Hola {emp.nombre},\n\nSe te ha asignado una nueva tarea: "{titulo}".\nFecha límite: {fecha_limite}\n\nDescripción: {descripcion}\n\nPor favor ingresa a tu agenda para gestionarla.',
                            settings.EMAIL_HOST_USER,
                            [emp.correo],
                            fail_silently=True
                        )
                    except:
                        pass
                    count += 1
                
                if count > 0:
                    messages.success(request, f'Se ha asignado la tarea a {count} empleados del cargo {cargo.nombre}.')
                else:
                    messages.warning(request, f'El cargo {cargo.nombre} no tiene empleados activos actualmente.')
            
            else:
                messages.error(request, 'Debes seleccionar un Cargo o un Empleado para asignar la tarea.')
                
        else:
            messages.error(request, 'No tienes los permisos o el cargo adecuado para crear tareas.')
        
        return redirect('gestion_tareas')

    data = {
        'tareas': tareas,
        'cargos': Cargo.objects.all(), # Para el select de crear tarea
        'empleados_filtro': lista_completa_empleados,
        'permisos': permisos,
        'nombre_rol': nombre_rol,
        'can_create_tasks': can_create_tasks,
        'usuario': usuario_profile,
        'empleado': empleado_profile,
        'usuarios': permisos.get('usuarios', 0), # Agregado para visibilidad del menú
    }
    return render(request, 'plantillas/tareas.html', data)

@login_required
def completar_tarea(request, id_tarea):
    if request.method == 'POST':
        tarea = get_object_or_404(Tarea, id_tarea=id_tarea)
        # Security check: only owner or admin can complete
        usuario_logeado_id = request.session.get('usuario_logeado')
        if not request.user.is_superuser and tarea.empleado.id != usuario_logeado_id:
            messages.error(request, "No tienes permiso para modificar esta tarea.")
            return redirect('agenda_personal')

        archivo = request.FILES.get('archivo_adjunto')
        comentarios = request.POST.get('comentarios_cumplimiento')

        if archivo:
            # Si ya existe un archivo, lo borramos antes de guardar el nuevo.
            if tarea.archivo_adjunto:
                tarea.archivo_adjunto.delete(save=False)
            tarea.archivo_adjunto = archivo
        
        if comentarios:
            tarea.comentarios_cumplimiento = comentarios

        tarea.completada = True
        tarea.save()
        messages.success(request, f"Tarea '{tarea.titulo}' completada exitosamente.")
    
    # Redirect logic: if admin, go to task management, if employee, go to personal agenda.
    referer = request.META.get('HTTP_REFERER')
    if request.user.is_superuser or (referer and 'ver_agenda' in referer):
        return redirect(referer or 'gestion_tareas')
    else:
        return redirect('agenda_personal')

@login_required
def reactivar_tarea(request, id_tarea):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para reactivar tareas.")
        return redirect('agenda_personal')

    tarea = get_object_or_404(Tarea, id_tarea=id_tarea)
    tarea.completada = False
    if tarea.archivo_adjunto:
        tarea.archivo_adjunto.delete(save=True) # Borra el archivo del almacenamiento
    else:
        tarea.save()
    messages.info(request, f"Tarea '{tarea.titulo}' ha sido reactivada.")
    return redirect('gestion_tareas')

@login_required
def eliminar_tarea(request, id_tarea):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user
    permisos = {}

    if user.is_superuser:
        permisos['eliminar'] = 1
    else:
        try:
            empleado_logeado = Empleado.objects.get(id=usuario_logeado_id)
            if empleado_logeado.id_rol:
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_logeado.id_rol)
                permisos = obtener_permisos(permisos_qs)
        except (Usuario.DoesNotExist, Empleado.DoesNotExist):
            pass

    if permisos.get('eliminar') == 1:
        tarea = get_object_or_404(Tarea, id_tarea=id_tarea)
        tarea.delete()
        messages.success(request, 'La tarea ha sido eliminada correctamente.')
    else:
        messages.error(request, 'No tienes permisos para eliminar tareas.')
    
    return redirect('gestion_tareas')

# -------------------------------- GESTIÓN DE CURSOS Y AGENDA PERSONAL --------------------------------

@login_required
def agenda_personal(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    
    # 1. Obtener el perfil del empleado
    try:
        empleado_profile = Empleado.objects.select_related('id_cargo', 'id_rol', 'user_id').get(id=usuario_logeado_id)
    except Empleado.DoesNotExist:
        # Si es superusuario pero no empleado, redirigir a una vista de admin
        if request.user.is_superuser:
            return redirect('gestion_cursos')
        messages.error(request, 'No se encontró tu perfil de empleado.')
        return redirect('index')

    # 2. Lógica de asignación automática de cursos obligatorios
    if empleado_profile.id_cargo:
        cursos_obligatorios = Curso.objects.filter(obligatorio_para=empleado_profile.id_cargo)
        
        # Optimización: Obtener IDs existentes primero para evitar consultas múltiples
        cursos_asignados_ids = EmpleadoCurso.objects.filter(
            empleado=empleado_profile,
            curso__in=cursos_obligatorios
        ).values_list('curso_id', flat=True)
        
        nuevos_cursos = []
        for curso in cursos_obligatorios:
            if curso.id_curso not in cursos_asignados_ids:
                nuevos_cursos.append(EmpleadoCurso(empleado=empleado_profile, curso=curso))
        
        if nuevos_cursos:
            EmpleadoCurso.objects.bulk_create(nuevos_cursos)

    # 3. Obtener Tareas y Cursos para la agenda
    # Filtramos tareas asignadas ESPECÍFICAMENTE a este empleado
    tareas_qs = Tarea.objects.filter(empleado=empleado_profile).order_by('fecha_limite')
    
    # --- Separación Pendientes vs Historial ---
    tareas_pendientes = [t for t in tareas_qs if not t.completada]
    tareas_historial = [t for t in tareas_qs if t.completada]
    
    # --- NOTIFICACIONES AUTOMÁTICAS ---
    today = timezone.now().date()
    
    # Alerta si hay tareas vencidas
    tareas_vencidas = sum(1 for t in tareas_pendientes if t.fecha_limite < today)
    if tareas_vencidas > 0:
        messages.warning(request, f'¡Atención! Tienes {tareas_vencidas} tareas operativas vencidas. Por favor gestiónalas.')
        
    # Alerta de tareas próximas a vencer (Próximos 3 días)
    limit_date = today + timedelta(days=3)
    tareas_proximas = sum(1 for t in tareas_pendientes if today <= t.fecha_limite <= limit_date)
    if tareas_proximas > 0:
        messages.info(request, f'Tienes {tareas_proximas} tareas que vencen en los próximos 3 días.')

    cursos_qs = EmpleadoCurso.objects.filter(empleado=empleado_profile).select_related('curso').order_by('curso__nombre')
    
    cursos_pendientes = [c for c in cursos_qs if c.estado != 'APROBADO']
    cursos_historial = [c for c in cursos_qs if c.estado == 'APROBADO']

    # --- ALERTAS DE CURSOS Y CERTIFICADOS ---
    # Alerta de cursos vencidos o próximos a vencer (en Historial/Aprobados)
    certs_por_vencer = 0
    for c in cursos_historial:
        if c.fecha_vencimiento and today <= c.fecha_vencimiento <= limit_date:
            certs_por_vencer += 1
    
    if certs_por_vencer > 0:
        messages.warning(request, f'¡Aviso! Tienes {certs_por_vencer} certificado(s) próximo(s) a vencer o vencidos.')
        
    # Alerta específica para cursos RECHAZADOS (Feedback de estado)
    rechazados_count = sum(1 for c in cursos_pendientes if c.estado == 'RECHAZADO')
    if rechazados_count > 0:
        messages.error(request, f'Atención: Tienes {rechazados_count} certificado(s) rechazado(s). Por favor revisa las observaciones y vuelve a subirlo.')

    # Alerta genérica de cursos pendientes (para motivar el avance)
    num_pendientes = len(cursos_pendientes)
    if num_pendientes > 0:
        messages.info(request, f'Recordatorio: Tienes {num_pendientes} cursos obligatorios pendientes por aprobar.')

    # --- LOGICA DE GAMIFICACIÓN ---
    total_asignados = len(cursos_qs)
    progreso_cumplimiento = 0
    if total_asignados > 0:
        progreso_cumplimiento = int((len(cursos_historial) / total_asignados) * 100)
    
    # --- CÁLCULO CUMPLIMIENTO TAREAS ---
    total_tareas = len(tareas_qs)
    progreso_tareas = 0
    if total_tareas > 0:
        progreso_tareas = int((len(tareas_historial) / total_tareas) * 100)
    
    # --- GAMIFICACIÓN AVANZADA ---
    # 1. Ranking por Área (Ubicación)
    ranking = 0
    total_area = 0
    if empleado_profile.id_ubicacion:
        # Optimizamos el cálculo del ranking usando anotaciones para evitar el problema N+1
        coleagas = Empleado.objects.filter(id_ubicacion=empleado_profile.id_ubicacion).annotate(
            c_ok=Count('cursos_asignados', filter=Q(cursos_asignados__estado='APROBADO'), distinct=True),
            t_ok=Count('tarea', filter=Q(tarea__completada=True), distinct=True)
        )
        total_area = coleagas.count()
        # Calculamos puntaje simple: (Cursos Aprobados * 10) + (Tareas Completadas * 5)
        scores = []
        for col in coleagas:
            puntos = (col.c_ok * 10) + (col.t_ok * 5)
            scores.append(puntos)
        
        scores.sort(reverse=True) # Ordenar descendente
        # Mi puntaje
        mi_puntaje = (len(cursos_historial) * 10) + (len(tareas_historial) * 5)
        # Encontrar mi posición (índice + 1)
        # Manejo simple de empates: tomamos la primera aparición
        ranking = scores.index(mi_puntaje) + 1 if mi_puntaje in scores else total_area

    # --- RETO MENSUAL (GAMIFICACIÓN) ---
    # Reto: "Operación Impecable" - Sin tareas vencidas y al menos 1 completada
    reto_mensual = {
        'titulo': 'Operación Impecable',
        'descripcion': 'Completa tareas este mes sin tener ninguna vencida.',
        'cumplido': False,
        'icono': 'fa-solid fa-shield-halved'
    }
    tareas_completadas_mes = [t for t in tareas_historial if t.fecha_creacion.month == today.month]
    tiene_vencidas = any(t.is_overdue for t in tareas_pendientes)
    if not tiene_vencidas and len(tareas_completadas_mes) > 0:
        reto_mensual['cumplido'] = True

    insignias = []
    # Insignia por Cumplimiento de Cursos
    if progreso_cumplimiento == 100 and total_asignados > 0:
        insignias.append({'icono': 'fa-solid fa-medal', 'color': 'text-warning', 'titulo': 'Excelencia Académica', 'desc': '100% de cursos aprobados'})
    elif progreso_cumplimiento >= 50:
        insignias.append({'icono': 'fa-solid fa-star-half-stroke', 'color': 'text-info', 'titulo': 'Buen Avance', 'desc': 'Más del 50% completado'})
    
    # Insignia por Tareas al día
    if not tareas_pendientes and tareas_historial:
        insignias.append({'icono': 'fa-solid fa-clipboard-check', 'color': 'text-success', 'titulo': 'Operativo Eficaz', 'desc': 'Sin tareas pendientes'})
    
    # Insignia de Bienvenida (si acaba de empezar)
    if progreso_cumplimiento == 0 and not tareas_historial:
        insignias.append({'icono': 'fa-regular fa-hand-peace', 'color': 'text-primary', 'titulo': 'Nuevo Ingreso', 'desc': '¡Bienvenido al equipo!'})
    # ------------------------------

    # 4. Obtener permisos y datos para el menú
    permisos = {}
    nombre_rol = "Empleado (Sin Rol)"
    if empleado_profile.id_rol:
        rol_nom = empleado_profile.id_rol.nombre
        nombre_rol = rol_nom
        permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
        permisos = obtener_permisos(permisos_qs)
    
    context = {
        'tareas_pendientes': tareas_pendientes,
        'tareas_historial': tareas_historial,
        'cursos_pendientes': cursos_pendientes,
        'cursos_historial': cursos_historial,
        'tareas': tareas_qs, # Necesario para generar los modales de todas las tareas
        'usuario': empleado_profile, # Empleado hereda de Usuario
        'empleado': empleado_profile,
        'nombre_rol': nombre_rol,
        'permisos': permisos,
        'usuarios': permisos.get('usuarios', 0),
        'today': today, # Añadimos la fecha de hoy para comparaciones en la plantilla
        'progreso_cumplimiento': progreso_cumplimiento,
        'insignias': insignias,
        'total_cursos': total_asignados,
        'progreso_tareas': progreso_tareas,
        'total_tareas': total_tareas,
        # Datos Gamificación
        'ranking_area': ranking,
        'total_area': total_area,
        'reto_mensual': reto_mensual,
    }
    
    return render(request, 'plantillas/agenda.html', context)

@login_required
def subir_certificado(request, id_empleado_curso):
    if request.method == 'POST':
        empleado_curso = get_object_or_404(EmpleadoCurso, id_empleado_curso=id_empleado_curso)
        
        # Verificar que el usuario que sube es el dueño del curso
        usuario_logeado_id = request.session.get('usuario_logeado')
        if empleado_curso.empleado.id != usuario_logeado_id:
            messages.error(request, "No tienes permiso para modificar este curso.")
            return redirect('agenda_personal')

        certificado_file = request.FILES.get('certificado')
        if certificado_file:
            # Borra el certificado anterior si existe
            if empleado_curso.certificado:
                empleado_curso.certificado.delete(save=False)

            empleado_curso.certificado = certificado_file
            empleado_curso.estado = 'EN_REVISION' # Cambia a estado de revisión
            empleado_curso.save()
            
            # Notificar al Administrador que llegó un nuevo certificado
            try:
                send_mail(
                    f"Certificado para Validar: {empleado_curso.empleado.nombre}",
                    f"El empleado {empleado_curso.empleado.nombre} ha enviado su certificado del curso '{empleado_curso.curso.nombre}'.\n\nPor favor ingrese al panel de 'Gestión de Cursos' para aprobarlo o rechazarlo.",
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER], # Se envía al correo principal del sistema (Admin)
                    fail_silently=True
                )
            except: pass

            messages.success(request, f"Tu certificado para '{empleado_curso.curso.nombre}' fue enviado para validación.")
        else:
            messages.error(request, "Debes seleccionar un archivo.")

    return redirect('agenda_personal')

@login_required
def eliminar_certificado(request, id_empleado_curso):
    if request.method == 'POST':
        empleado_curso = get_object_or_404(EmpleadoCurso, id_empleado_curso=id_empleado_curso)
        
        usuario_logeado_id = request.session.get('usuario_logeado')
        if empleado_curso.empleado.id != usuario_logeado_id:
            messages.error(request, "No tienes permiso para modificar este curso.")
            return redirect('agenda_personal')

        if empleado_curso.certificado:
            empleado_curso.certificado.delete(save=False)
            empleado_curso.certificado = None
            empleado_curso.estado = 'PENDIENTE' # Reiniciamos el estado para que pueda subir uno nuevo
            empleado_curso.save()
            messages.success(request, f"Archivo eliminado. El curso vuelve a estado Pendiente.")
    
    return redirect('agenda_personal')

@login_required
def soporte_empleado(request):
    """Procesa el formulario de soporte enviado por el empleado."""
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        usuario = request.user # Usuario de Django (auth_user)
        
        # Preparamos el cuerpo del correo
        cuerpo_correo = f"""
        Solicitud de Soporte enviada desde el Portal de Empleados.
        
        Usuario: {usuario.username}
        Correo: {usuario.email}
        
        Mensaje:
        {mensaje}
        """
        
        try:
            # Enviar correo al administrador (usando el correo configurado en settings)
            send_mail(
                subject=f"Soporte Empleado: {asunto}",
                message=cuerpo_correo,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER], # Se envía al admin
                fail_silently=False,
            )
            messages.success(request, 'Tu solicitud de soporte ha sido enviada al administrador.')
        except Exception as e:
            print(f"Error enviando soporte: {e}")
            messages.error(request, 'Hubo un error al enviar tu solicitud. Por favor intenta más tarde o contacta por otro medio.')
            
    return redirect('agenda_personal')

@login_required
def gestion_cursos(request):
    # --- Verificación de permisos de Administrador ---
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user
    permisos = {}
    empleado_profile = None
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado_profile = Empleado.objects.get(id=usuario_profile.id)
        except Empleado.DoesNotExist:
            pass
    else:
        try:
            empleado_profile = Empleado.objects.get(id=usuario_logeado_id)
            # PERMITIR ACCESO: Si tiene rol, cargamos sus permisos (aunque sean solo lectura)
            if empleado_profile.id_rol:
                rol_nom = empleado_profile.id_rol.nombre
                nombre_rol = rol_nom
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                # Si no tiene rol, entra sin permisos (todo en 0)
                nombre_rol = "Empleado (Sin Rol)"
                permisos = {'crear': 0, 'editar': 0, 'eliminar': 0, 'consultar': 1}

        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # Lógica para crear/editar un curso
    if request.method == 'POST':
        # Validación de seguridad extra para POST
        if permisos.get('crear') != 1 and permisos.get('editar') != 1:
            messages.error(request, 'No tienes permisos para realizar cambios.')
            return redirect('gestion_cursos')

        nombre_curso = request.POST.get('nombre_curso')
        descripcion_curso = request.POST.get('descripcion_curso')
        external_url = request.POST.get('external_url')
        modalidad = request.POST.get('modalidad')
        lugar = request.POST.get('lugar')
        periodicidad = request.POST.get('periodicidad')
        cargos_obligatorios_ids = request.POST.getlist('cargos_obligatorios')

        if nombre_curso:
            curso, created = Curso.objects.get_or_create(nombre=nombre_curso)
            curso.descripcion = descripcion_curso
            if modalidad:
                curso.modalidad = modalidad
            curso.lugar = lugar # Guardar lugar (puede ser vacío si es virtual)
            if periodicidad:
                curso.periodicidad = periodicidad
            curso.external_url = external_url
            curso.obligatorio_para.set(cargos_obligatorios_ids)
            curso.save()
            
            # Asignar automáticamente el curso a los empleados existentes de esos cargos
            empleados_afectados = Empleado.objects.filter(id_cargo__in=cargos_obligatorios_ids)
            for emp in empleados_afectados:
                obj, created = EmpleadoCurso.objects.get_or_create(empleado=emp, curso=curso)
                if created:
                    # Notificar nueva asignación
                    try:
                        send_mail(
                            'Nuevo Curso Asignado - Petrocentro',
                            f'Hola {emp.nombre},\n\nSe te ha asignado el curso obligatorio "{nombre_curso}". Por favor ingresa a tu agenda para gestionarlo.\n\nSaludos.',
                            settings.EMAIL_HOST_USER,
                            [emp.correo],
                            fail_silently=True
                        )
                    except:
                        pass

            messages.success(request, f"Curso '{nombre_curso}' guardado y asignado correctamente.")
            return redirect('gestion_cursos')

    # Lógica para mostrar la vista
    cursos = Curso.objects.prefetch_related('obligatorio_para').all()
    cargos = Cargo.objects.all()
    certificados_pendientes = EmpleadoCurso.objects.filter(estado='EN_REVISION').select_related('empleado', 'curso', 'empleado__user_id')
    
    # --- RECORDATORIOS DE RENOVACIÓN (Cursos por Vencer o Vencidos) ---
    fecha_limite_recordatorio = timezone.now().date() + timedelta(days=30) # Vencen en los próximos 30 días o ya vencieron
    renovaciones_pendientes = EmpleadoCurso.objects.filter(estado='APROBADO', fecha_vencimiento__lte=fecha_limite_recordatorio).select_related('empleado', 'curso', 'empleado__id_cargo').order_by('fecha_vencimiento')

    
    # --- Filtros Avanzados para Certificados Pendientes ---
    pend_curso = request.GET.get('pend_curso')
    pend_cargo = request.GET.get('pend_cargo')
    
    if pend_curso:
        certificados_pendientes = certificados_pendientes.filter(curso__id_curso=pend_curso)
    if pend_cargo:
        certificados_pendientes = certificados_pendientes.filter(empleado__id_cargo__id_cargo=pend_cargo)

    # --- INDICADORES DASHBOARD (KPIs) ---
    # Se calculan totales globales para gráficas y métricas
    total_asignaciones = EmpleadoCurso.objects.count()
    total_aprobados = EmpleadoCurso.objects.filter(estado='APROBADO').count()
    porcentaje_cumplimiento = (total_aprobados / total_asignaciones * 100) if total_asignaciones > 0 else 0
    pendientes_revision_count = EmpleadoCurso.objects.filter(estado='EN_REVISION').count()
    cursos_activos_count = Curso.objects.count()
    pendientes_realizar = EmpleadoCurso.objects.filter(estado='PENDIENTE').count()

    # --- INDICADORES TAREAS (NUEVO PARA DASHBOARD GLOBAL) ---
    total_tareas_asignadas = Tarea.objects.count()
    tareas_completadas_count = Tarea.objects.filter(completada=True).count()
    tareas_pendientes_count = Tarea.objects.filter(completada=False).count()
    cumplimiento_tareas_global = (tareas_completadas_count / total_tareas_asignadas * 100) if total_tareas_asignadas > 0 else 0

    # --- DATOS PARA GRÁFICAS (Chart.js) ---
    # 1. Estado Global (Pie Chart)
    estados_agrupados = EmpleadoCurso.objects.values('estado').annotate(total=Count('estado'))
    datos_estados = {est['estado']: est['total'] for est in estados_agrupados}
    
    grafica_global = {
        'labels': ['Aprobado (Cumplido)', 'En Revisión', 'Pendiente', 'Rechazado'],
        'data': [
            datos_estados.get('APROBADO', 0),
            datos_estados.get('EN_REVISION', 0),
            datos_estados.get('PENDIENTE', 0),
            datos_estados.get('RECHAZADO', 0)
        ],
    }

    # 2. Cumplimiento por Cargo (Bar Chart)
    cumplimiento_cargos = EmpleadoCurso.objects.values('empleado__id_cargo__nombre').annotate(
        total=Count('id_empleado_curso'),
        aprobados=Count(Case(When(estado='APROBADO', then=1), output_field=IntegerField()))
    ).order_by('empleado__id_cargo__nombre').exclude(empleado__id_cargo__nombre__isnull=True)

    cargos_labels = []
    cargos_data = []
    for c in cumplimiento_cargos:
        cargos_labels.append(c['empleado__id_cargo__nombre'])
        val = round((c['aprobados'] / c['total'] * 100), 1) if c['total'] > 0 else 0
        cargos_data.append(val)

    # 3. Cumplimiento por Área (Ubicación)
    cumplimiento_areas = EmpleadoCurso.objects.values('empleado__id_ubicacion__nombre').annotate(
        total=Count('id_empleado_curso'),
        aprobados=Count(Case(When(estado='APROBADO', then=1), output_field=IntegerField()))
    ).order_by('empleado__id_ubicacion__nombre').exclude(empleado__id_ubicacion__nombre__isnull=True)

    areas_labels = []
    areas_data = []
    for a in cumplimiento_areas:
        areas_labels.append(a['empleado__id_ubicacion__nombre'])
        val = round((a['aprobados'] / a['total'] * 100), 1) if a['total'] > 0 else 0
        areas_data.append(val)

    # --- Lógica de Supervisión (Matriz de Cumplimiento) ---
    # Filtros para la tabla general de seguimiento
    estado_filtro = request.GET.get('estado')
    curso_filtro = request.GET.get('curso')
    cargo_filtro = request.GET.get('cargo')
    
    seguimiento = EmpleadoCurso.objects.select_related('empleado', 'curso', 'empleado__id_cargo').all()
    
    if estado_filtro:
        seguimiento = seguimiento.filter(estado=estado_filtro)
    if curso_filtro:
        seguimiento = seguimiento.filter(curso__id_curso=curso_filtro)
    if cargo_filtro:
        seguimiento = seguimiento.filter(empleado__id_cargo_id=cargo_filtro)
        
    seguimiento = seguimiento.order_by('empleado__nombre', 'curso__nombre')

    context = {
        'cursos': cursos,
        'cargos': cargos,
        'certificados_pendientes': certificados_pendientes,
        'renovaciones_pendientes': renovaciones_pendientes,
        'seguimiento': seguimiento,
        'stats': {
            'cumplimiento': round(porcentaje_cumplimiento, 1),
            'pendientes_revision': pendientes_revision_count,
            'total_asignaciones': total_asignaciones,
            'cursos_activos': cursos_activos_count,
            'pendientes_realizar': pendientes_realizar,
            # KPIs de Tareas
            'total_tareas': total_tareas_asignadas,
            'cumplimiento_tareas': round(cumplimiento_tareas_global, 1),
            'tareas_pendientes': tareas_pendientes_count
        },
        'graficas': {
            'global': json.dumps(grafica_global),
            'cargos_labels': json.dumps(cargos_labels),
            'cargos_data': json.dumps(cargos_data),
            # Datos para gráfica de áreas
            'areas_labels': json.dumps(areas_labels),
            'areas_data': json.dumps(areas_data),
        },
        'filtros_pendientes': {'curso': pend_curso, 'cargo': pend_cargo},
        'usuario': usuario_profile,
        'empleado': empleado_profile,
        'nombre_rol': "Administrador",
        'permisos': permisos,
        'usuarios': permisos.get('usuarios', 0), # Agregado para visibilidad del menú
    }
    return render(request, 'plantillas/gestion_cursos_obligatorios.html', context)

@login_required
def validar_certificado(request, id_empleado_curso):
    # --- Verificación de Permisos (Rol Granular) ---
    # Se permite validar a Superusuarios O a empleados con permiso 'Editar' (ej. Supervisor/Validador)
    usuario_logeado_id = request.session.get('usuario_logeado')
    can_validate = False
    
    if request.user.is_superuser:
        can_validate = True
    else:
        # Verificar si tiene permiso de 'Editar' en sus roles
        rol_perms = Rol_permiso.objects.filter(rol__empleado__id=usuario_logeado_id, permiso__nombre__in=['Editar', 'Actualizar'])
        if rol_perms.exists():
            can_validate = True
            
    if not can_validate:
        messages.error(request, "No tienes permiso para validar certificados.")
        return redirect('gestion_cursos')

    if request.method == 'POST':
        empleado_curso = get_object_or_404(EmpleadoCurso, id_empleado_curso=id_empleado_curso)
        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')

        if accion == 'aprobar':
            empleado_curso.estado = 'APROBADO'
            empleado_curso.comentarios_revision = ''
            
            # Calcular fecha de vencimiento automática según periodicidad
            if empleado_curso.curso.periodicidad == 'ANUAL':
                empleado_curso.fecha_vencimiento = timezone.now().date() + timedelta(days=365)
            elif empleado_curso.curso.periodicidad == 'SEMESTRAL':
                empleado_curso.fecha_vencimiento = timezone.now().date() + timedelta(days=180)
            elif empleado_curso.curso.periodicidad == 'MENSUAL':
                empleado_curso.fecha_vencimiento = timezone.now().date() + timedelta(days=30)
            # Si es UNICO, se mantiene la fecha que tuviera o null
            
            empleado_curso.save()
            
            # Notificación Automática al Empleado
            try:
                send_mail(
                    'Certificado Aprobado - Petrocentro',
                    f'Hola {empleado_curso.empleado.nombre},\n\nTu certificado del curso "{empleado_curso.curso.nombre}" ha sido aprobado exitosamente.\n\nAtentamente,\nEquipo de Formación.',
                    settings.EMAIL_HOST_USER,
                    [empleado_curso.empleado.correo],
                    fail_silently=True
                )
            except Exception:
                pass
                
            messages.success(request, f"Certificado de {empleado_curso.empleado.nombre} APROBADO.")
        elif accion == 'rechazar':
            empleado_curso.estado = 'RECHAZADO'
            empleado_curso.comentarios_revision = comentarios
            if empleado_curso.certificado:
                empleado_curso.certificado.delete(save=False)
            empleado_curso.save()
            
            # Notificación Automática de Rechazo
            try:
                send_mail(
                    'Certificado Rechazado - Petrocentro',
                    f'Hola {empleado_curso.empleado.nombre},\n\nTu certificado del curso "{empleado_curso.curso.nombre}" ha sido rechazado.\n\nMotivo: {comentarios}\n\nPor favor ingresa a la plataforma y sube el documento correcto.',
                    settings.EMAIL_HOST_USER,
                    [empleado_curso.empleado.correo],
                    fail_silently=True
                )
            except Exception:
                pass
                
            messages.warning(request, f"Certificado de {empleado_curso.empleado.nombre} RECHAZADO.")
    
    return redirect('gestion_cursos')

@login_required
def editar_curso(request, id_curso):
    # Verificación de permisos básica (similar a gestion_cursos)
    if not request.user.is_superuser:
        try:
            emp = Empleado.objects.get(id=request.session.get('usuario_logeado'))
            if not emp.id_rol or emp.id_rol.nombre != 'Administrador':
                messages.error(request, 'No tienes permisos.')
                return redirect('gestion_cursos')
        except:
            return redirect('index')

    curso = get_object_or_404(Curso, id_curso=id_curso)
    
    if request.method == 'POST':
        nombre_curso = request.POST.get('nombre_curso')
        descripcion_curso = request.POST.get('descripcion_curso')
        external_url = request.POST.get('external_url')
        modalidad = request.POST.get('modalidad')
        lugar = request.POST.get('lugar')
        periodicidad = request.POST.get('periodicidad')
        cargos_obligatorios_ids = request.POST.getlist('cargos_obligatorios')

        if nombre_curso:
            curso.nombre = nombre_curso
            curso.descripcion = descripcion_curso
            if modalidad:
                curso.modalidad = modalidad
            curso.lugar = lugar
            if periodicidad:
                curso.periodicidad = periodicidad
            curso.external_url = external_url
            curso.obligatorio_para.set(cargos_obligatorios_ids)
            curso.save()
            
            # Actualizar asignaciones a empleados
            empleados_afectados = Empleado.objects.filter(id_cargo__in=cargos_obligatorios_ids)
            emails_count = 0
            for emp in empleados_afectados:
                obj, created = EmpleadoCurso.objects.get_or_create(empleado=emp, curso=curso)
                if created:
                    # Notificar nueva asignación
                    try:
                        send_mail(
                            'Nuevo Curso Asignado - Petrocentro',
                            f'Hola {emp.nombre},\n\nSe te ha asignado el curso obligatorio "{curso.nombre}". Por favor ingresa a tu agenda para gestionarlo.\n\nSaludos.',
                            settings.EMAIL_HOST_USER,
                            [emp.correo],
                            fail_silently=True
                        )
                    except:
                        pass
            
            messages.success(request, f"Curso '{nombre_curso}' actualizado correctamente.")
            return redirect('gestion_cursos')

    # Contexto para el formulario de edición
    context = {
        'curso': curso,
        'cargos': Cargo.objects.all(),
        'usuario': get_object_or_404(Usuario, id=request.session.get('usuario_logeado')), # Corregido para foto perfil
        'usuarios': 1, # Admin tiene permisos de usuario por defecto
        'nombre_rol': "Administrador",
        # Pre-seleccionar cargos
        'cargos_seleccionados': curso.obligatorio_para.values_list('id_cargo', flat=True)
    }
    return render(request, 'plantillas/editar_curso.html', context)

@login_required
def eliminar_curso(request, id_curso):
    # Verificación de permisos
    if not request.user.is_superuser:
        # Agregar lógica de verificación de rol si es necesario
        pass

    curso = get_object_or_404(Curso, id_curso=id_curso)
    
    try:
        curso.delete()
        messages.success(request, 'Curso eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el curso: {e}')
    
    return redirect('gestion_cursos')

# -------------------------------- PERFILES DE ROL (REDIRECCIÓN Y VISTAS PRINCIPALES) --------------------------------

@login_required
def perfil_empleado(request):
    """Vista principal para el rol de Empleado: Muestra Agenda (Tareas + Cursos)"""
    return agenda_personal(request)

@login_required
def perfil_admin(request):
    """Vista principal para el rol de Administrador: Herramientas de Gestión (Cursos, Certificados)"""
    return gestion_cursos(request)

@login_required
def ver_agenda_empleado(request, empleado_id):
    """
    Vista para que un Administrador vea la agenda de un empleado específico.
    """
    # 1. Check if logged-in user is an admin
    if not request.user.is_superuser:
        # Aquí se podría añadir una verificación de rol más granular si es necesario
        messages.error(request, "No tienes permisos para ver la agenda de otros empleados.")
        return redirect('empleados')

    # 2. Get the target employee's profile
    try:
        empleado_profile = Empleado.objects.select_related('id_cargo', 'id_rol', 'user_id').get(id=empleado_id)
    except Empleado.DoesNotExist:
        messages.error(request, 'El empleado solicitado no existe.')
        return redirect('empleados')

    # 3. Reuse the logic from agenda_personal to get tasks and courses
    tareas_qs = Tarea.objects.filter(empleado=empleado_profile).order_by('fecha_limite')
    cursos_qs = EmpleadoCurso.objects.filter(empleado=empleado_profile).select_related('curso').order_by('curso__nombre')

    tareas_pendientes = [t for t in tareas_qs if not t.completada]
    tareas_historial = [t for t in tareas_qs if t.completada]
    
    cursos_pendientes = [c for c in cursos_qs if c.estado != 'APROBADO']
    cursos_historial = [c for c in cursos_qs if c.estado == 'APROBADO']

    # Cálculos para la vista (Admin viendo Empleado)
    total_asignados = len(cursos_qs)
    progreso_cumplimiento = 0
    if total_asignados > 0:
        progreso_cumplimiento = int((len(cursos_historial) / total_asignados) * 100)
        
    total_tareas = len(tareas_qs)
    progreso_tareas = 0
    if total_tareas > 0:
        progreso_tareas = int((len(tareas_historial) / total_tareas) * 100)

    # 4. Prepare context for the template
    admin_profile = get_object_or_404(Usuario, id=request.session.get('usuario_logeado'))
    
    context = {
        'tareas_pendientes': tareas_pendientes,
        'tareas_historial': tareas_historial,
        'cursos_pendientes': cursos_pendientes,
        'cursos_historial': cursos_historial,
        'tareas': tareas_qs, # Modals
        'usuario': admin_profile,       # The logged-in admin for the navbar
        'empleado': empleado_profile,   # The employee being viewed
        'nombre_rol': "Administrador",  # The role of the viewer
        'is_admin_view': True,          # A flag to adjust the template for admin viewing
        'usuarios': 1,                  # Admin permissions for menu
        'today': timezone.now().date(),
        'progreso_cumplimiento': progreso_cumplimiento,
        'total_cursos': total_asignados,
        'progreso_tareas': progreso_tareas,
        'total_tareas': total_tareas,
    }
    
    return render(request, 'plantillas/agenda.html', context)

@login_required
def exportar_matriz_excel(request):
    # Permission check
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para exportar reportes.")
        return redirect('gestion_cursos')

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Matriz de Cumplimiento'

    estado_filtro = request.GET.get('estado')
    curso_filtro = request.GET.get('curso')
    cargo_filtro = request.GET.get('cargo')
    
    seguimiento = EmpleadoCurso.objects.select_related('empleado', 'curso', 'empleado__id_cargo').all()
    if estado_filtro: seguimiento = seguimiento.filter(estado=estado_filtro)
    if curso_filtro: seguimiento = seguimiento.filter(curso__id_curso=curso_filtro)
    if cargo_filtro: seguimiento = seguimiento.filter(empleado__id_cargo_id=cargo_filtro)
    seguimiento = seguimiento.order_by('empleado__nombre', 'curso__nombre')

    headers = ['Empleado', 'Identificación', 'Cargo', 'Curso Obligatorio', 'Estado', 'Fecha de Vencimiento']
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    for item in seguimiento:
        sheet.append([item.empleado.nombre, item.empleado.identificacion, item.empleado.id_cargo.nombre, item.curso.nombre, item.get_estado_display(), item.fecha_vencimiento.strftime('%Y-%m-%d') if item.fecha_vencimiento else 'N/A'])

    for col_letter in ['A', 'B', 'C', 'D', 'E', 'F']: sheet.column_dimensions[col_letter].autosize = True

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="matriz_cumplimiento.xlsx"'
    workbook.save(response)
    return response

@login_required
def descargar_pdf_empleados(request):
    # Obtener empleados (podrías aplicar los mismos filtros que en la lista si lo deseas)
    empleados = Empleado.objects.all().order_by('nombre')
    
    # Contexto para la plantilla PDF
    context = {
        'empleados': empleados,
        'fecha': timezone.now(),
        'titulo': 'Listado de Empleados - Petrocentro'
    }
    
    # Renderizar plantilla y crear PDF
    template_path = 'dash/lista_empleados_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="listado_empleados.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

@login_required
def exportar_empleados_excel(request):
    # Filtros
    busqueda = request.GET.get("buscar") 
    estado = request.GET.get("estado")
    filtro_cargo = request.GET.get("cargo")
    filtro_ubicacion = request.GET.get("ubicacion")

    lista_empleados = Empleado.objects.select_related('id_cargo', 'id_rol', 'id_ubicacion', 'estado').all()

    if estado and estado != "0":
        lista_empleados = lista_empleados.filter(estado=estado)
    if filtro_cargo and filtro_cargo != '0':
        lista_empleados = lista_empleados.filter(id_cargo_id=filtro_cargo)
    if filtro_ubicacion and filtro_ubicacion != '0':
        lista_empleados = lista_empleados.filter(id_ubicacion_id=filtro_ubicacion)
    if busqueda:
        lista_empleados = lista_empleados.filter(
            Q(nombre__icontains=busqueda) | Q(identificacion__icontains=busqueda)
        )

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Empleados'

    headers = ['ID', 'Nombre', 'Identificación', 'Correo', 'Teléfono', 'Cargo', 'Ubicación', 'Rol', 'Estado', 'Ingreso']
    sheet.append(headers)
    for cell in sheet[1]: cell.font = Font(bold=True)

    for e in lista_empleados:
        rol_nombre = e.id_rol.nombre if e.id_rol else 'Sin Rol'
        rol = rol_nombre
        estado_nombre = e.estado.nombre if e.estado else 'N/A'
        sheet.append([e.id, e.nombre, e.identificacion, e.correo, e.telefono, e.id_cargo.nombre, e.id_ubicacion.nombre, rol, estado_nombre, e.fecha_ingreso])

    for col in ['B', 'D', 'F', 'G']: sheet.column_dimensions[col].autosize = True

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="empleados_filtrados.xlsx"'
    workbook.save(response)
    return response

@login_required
def asignar_curso_empleado(request, id_empleado):
    if request.method == 'POST':
        empleado = get_object_or_404(Empleado, id=id_empleado)
        curso_id = request.POST.get('curso')
        
        if curso_id:
            curso = get_object_or_404(Curso, id_curso=curso_id)
            obj, created = EmpleadoCurso.objects.get_or_create(empleado=empleado, curso=curso)
            if created:
                messages.success(request, f"Curso '{curso.nombre}' asignado a {empleado.nombre}.")
                # Notificación por correo
                try:
                    send_mail(
                        'Nuevo Curso Asignado - Petrocentro',
                        f'Hola {empleado.nombre},\n\nSe te ha asignado el curso obligatorio "{curso.nombre}".\nPor favor ingresa a la plataforma para gestionarlo.\n\nAtentamente,\nEquipo de Formación.',
                        settings.EMAIL_HOST_USER,
                        [empleado.correo],
                        fail_silently=True
                    )
                except:
                    pass
                # Log
                LogActividad.objects.create(usuario_afectado=empleado, admin_responsable=Usuario.objects.get(id=request.session.get('usuario_logeado')), accion="Asignación Manual Curso", detalles=f"Curso: {curso.nombre}")
            else:
                messages.warning(request, f"El empleado ya tiene asignado el curso '{curso.nombre}'.")
    
    return redirect('empleados')

@login_required
def enviar_notificacion_empleado(request, id_empleado):
    if request.method == 'POST':
        empleado = get_object_or_404(Empleado, id=id_empleado)
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        try:
            send_mail(
                f"Notificación Petrocentro: {asunto}",
                f"Hola {empleado.nombre},\n\n{mensaje}\n\nAtentamente,\nAdministración.",
                settings.EMAIL_HOST_USER,
                [empleado.correo],
                fail_silently=False
            )
            messages.success(request, f"Correo enviado a {empleado.nombre}.")
            
            LogActividad.objects.create(usuario_afectado=empleado, admin_responsable=Usuario.objects.get(id=request.session.get('usuario_logeado')), accion="Notificación Enviada", detalles=f"Asunto: {asunto}")
        except Exception as e:
            messages.error(request, f"Error al enviar correo: {e}")
            
    return redirect('empleados')

@login_required
def crear_tarea_rapida_empleado(request, id_empleado):
    if request.method == 'POST':
        # Verificar permisos (mismos que gestion_tareas)
        if not request.user.is_superuser: # Simplificado, agregar lógica de rol si necesario
             pass 

        empleado = get_object_or_404(Empleado, id=id_empleado)
        titulo = request.POST.get('titulo')
        fecha = request.POST.get('fecha_limite')
        desc = request.POST.get('descripcion')
        
        Tarea.objects.create(
            titulo=titulo,
            descripcion=desc,
            fecha_limite=fecha,
            id_cargo=empleado.id_cargo,
            empleado=empleado
        )
        # Notificación por correo
        try:
            send_mail(
                'Nueva Tarea Asignada - Petrocentro',
                f'Hola {empleado.nombre},\n\nSe te ha asignado una nueva tarea: "{titulo}".\nFecha límite: {fecha}\n\nDescripción: {desc}\n\nPor favor ingresa a tu agenda para gestionarla.',
                settings.EMAIL_HOST_USER,
                [empleado.correo],
                fail_silently=True
            )
        except:
            pass
        messages.success(request, f"Tarea asignada a {empleado.nombre}.")
        
    return redirect('empleados')

@login_required
def descargar_pdf_cumplimiento(request):
    # Verificación de permisos (Admin o Supervisor)
    if not request.user.is_superuser:
        usuario_logeado_id = request.session.get('usuario_logeado')
        has_perm = Rol_permiso.objects.filter(rol__empleado__id=usuario_logeado_id, permiso__nombre='Consultar').exists()
        if not has_perm:
            messages.error(request, "No tienes permisos para descargar este reporte.")
            return redirect('gestion_cursos')

    # Obtener datos de cumplimiento
    cursos_asignados = EmpleadoCurso.objects.select_related('empleado', 'curso', 'empleado__id_cargo').all().order_by('empleado__id_cargo__nombre', 'empleado__nombre')
    
    # Calculos básicos para el reporte
    total = cursos_asignados.count()
    aprobados = cursos_asignados.filter(estado='APROBADO').count()
    porcentaje = (aprobados / total * 100) if total > 0 else 0

    context = {
        'registros': cursos_asignados,
        'fecha': timezone.now(),
        'titulo': 'Reporte de Cumplimiento de Formación',
        'resumen': {'total': total, 'aprobados': aprobados, 'porcentaje': round(porcentaje, 1)}
    }
    
    template_path = 'dash/reporte_cumplimiento_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_cumplimiento.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

@login_required
def descargar_pdf_usuarios(request):
    usuarios = Usuario.objects.all().order_by('nombre')
    
    context = {
        'usuarios': usuarios,
        'fecha': timezone.now(),
        'titulo': 'Reporte de Usuarios del Sistema'
    }
    
    template_path = 'dash/lista_usuarios_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="listado_usuarios.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

@login_required
def notificar_vencimiento_curso(request, id_empleado_curso):
    # Verificar permisos básicos (Admin o Supervisor)
    if not request.user.is_superuser:
        # Agregar lógica adicional de roles si es necesario
        pass

    item = get_object_or_404(EmpleadoCurso, id_empleado_curso=id_empleado_curso)
    
    try:
        asunto = f"Alerta de Vencimiento: {item.curso.nombre}"
        mensaje = f"Hola {item.empleado.nombre},\n\nEste es un aviso automático para informarle que su certificado del curso obligatorio '{item.curso.nombre}' está próximo a vencer el día {item.fecha_vencimiento}.\n\nPor favor, gestione su renovación lo antes posible para mantener su cumplimiento al día.\n\nAtentamente,\nGestión Humana y HSEQ."
        
        send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [item.empleado.correo], fail_silently=False)
        
        LogActividad.objects.create(usuario_afectado=item.empleado, admin_responsable=Usuario.objects.get(id=request.session.get('usuario_logeado')), accion="Recordatorio Vencimiento", detalles=f"Curso: {item.curso.nombre}")
        messages.success(request, f"Recordatorio de vencimiento enviado a {item.empleado.nombre}.")
    except Exception as e:
        messages.error(request, f"Error al enviar correo: {e}")

    return redirect('gestion_cursos')

@login_required
def notificar_vencimiento_masivo(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('gestion_cursos')

    fecha_limite = timezone.now().date() + timedelta(days=30)
    pendientes = EmpleadoCurso.objects.filter(estado='APROBADO', fecha_vencimiento__lte=fecha_limite).select_related('empleado', 'curso')

    count = 0
    for item in pendientes:
        try:
            send_mail(
                f"Aviso de Vencimiento: {item.curso.nombre}",
                f"Hola {item.empleado.nombre},\n\nTu certificado del curso '{item.curso.nombre}' vence el {item.fecha_vencimiento}. Por favor gestiona su renovación.\n\nAtentamente,\nAdministración.",
                settings.EMAIL_HOST_USER,
                [item.empleado.correo],
                fail_silently=True
            )
            count += 1
        except: pass
    
    if count > 0:
        messages.success(request, f"Se han enviado {count} correos de recordatorio masivo.")
    else:
        messages.info(request, "No se enviaron correos (lista vacía o errores).")
        
    return redirect('gestion_cursos')

# -------------------------------- API CHAT INTERNO --------------------------------

@login_required
def chat_api(request):
    """Maneja el envío y recepción de mensajes vía AJAX"""
    # Intentar obtener usuario de la sesión, si falla, buscar por el usuario de Django
    usuario_id = request.session.get('usuario_logeado')
    
    if not usuario_id:
        try:
            usuario = Usuario.objects.get(user_id=request.user)
        except Usuario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no identificado'}, status=404)
    else:
        usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        if mensaje:
            es_admin = request.user.is_superuser
            MensajeChat.objects.create(usuario=usuario, mensaje=mensaje, es_respuesta_admin=es_admin)
            return JsonResponse({'status': 'ok'})
    
    # GET: Obtener últimos 50 mensajes (Chat Global Simplificado para Demo)
    if request.user.is_superuser:
        mensajes = MensajeChat.objects.select_related('usuario').order_by('-fecha')[:50]
    else:
        # El empleado ve sus mensajes y las respuestas globales de admin
        mensajes = MensajeChat.objects.filter(Q(usuario=usuario) | Q(es_respuesta_admin=True)).select_related('usuario').order_by('-fecha')[:50]
        
    data = []
    for m in reversed(list(mensajes)):
        data.append({
            'user': m.usuario.nombre,
            'text': m.mensaje,
            'is_me': m.usuario.id == usuario.id,
            'time': m.fecha.strftime('%H:%M'),
            'es_admin': m.es_respuesta_admin
        })
    
    return JsonResponse({'mensajes': data})

# -------------------------------- PANELES DE AUDITORÍA Y RRHH --------------------------------

@login_required
def panel_auditoria(request):
    if not request.user.is_superuser:
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')
        
    logs = LogActividad.objects.select_related('usuario_afectado', 'admin_responsable').all().order_by('-fecha')[:200]
    
    # Contexto para mantener el menú lateral correcto
    usuario_logeado_id = request.session.get('usuario_logeado')
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
    
    context = {
        'logs': logs,
        'usuario': usuario_profile,
        'nombre_rol': "Administrador",
        'usuarios': 1, # Activa las opciones de gestión en el menú
    }
    return render(request, 'dash/auditoria.html', context)

@login_required
def reporte_rrhh(request):
    if not request.user.is_superuser:
        messages.error(request, "Acceso restringido.")
        return redirect('index')

    # Optimizamos reporte RRHH con anotaciones masivas en una sola consulta
    empleados = Empleado.objects.select_related('id_cargo', 'id_ubicacion').annotate(
        total_c=Count('cursos_asignados', distinct=True),
        aprob_c=Count('cursos_asignados', filter=Q(cursos_asignados__estado='APROBADO'), distinct=True),
        total_t=Count('tarea', distinct=True),
        aprob_t=Count('tarea', filter=Q(tarea__completada=True), distinct=True)
    )
    reporte = []
    
    for emp in empleados:
        # Usamos los datos ya calculados por la base de datos
        perc_c = (emp.aprob_c / emp.total_c * 100) if emp.total_c > 0 else 0
        perc_t = (emp.aprob_t / emp.total_t * 100) if emp.total_t > 0 else 0
        
        reporte.append({'empleado': emp, 'curso_pct': round(perc_c,1), 'tarea_pct': round(perc_t,1), 'promedio': round((perc_c+perc_t)/2, 1)})
    
    # Contexto para mantener el menú lateral correcto
    usuario_logeado_id = request.session.get('usuario_logeado')
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
    
    context = {
        'reporte': reporte,
        'usuario': usuario_profile,
        'nombre_rol': "Administrador",
        'usuarios': 1
    }
    return render(request, 'dash/rrhh_reporte.html', context)

@login_required
def gestion_pqrs(request):
    """Vista para que el Administrador gestione todas las PQRS."""
    usuario_logeado_id = request.session.get('usuario_logeado')
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
    
    # Verificación de Rol Administrador
    if not request.user.is_superuser:
        try:
            empleado = Empleado.objects.get(id=usuario_profile.id)
            if not (empleado.id_rol and empleado.id_rol.nombre == "Administrador"):
                messages.error(request, "No tienes permisos para este módulo.")
                return redirect('index')
        except Empleado.DoesNotExist:
            return redirect('index')

    pqrs_qs = PQRS.objects.all().order_by('-fecha_creacion')
    
    # Filtros simples
    estado_f = request.GET.get('estado')
    if estado_f:
        pqrs_qs = pqrs_qs.filter(estado=estado_f)

    p = Paginator(pqrs_qs, 10)
    pagina = p.get_page(request.GET.get('page'))

    context = {
        'pqrs_list': pagina,
        'usuario': usuario_profile,
        'nombre_rol': "Administrador",
        'usuarios': 1, # Mantiene la visibilidad del menú
        'estados': PQRS.ESTADOS,
    }
    return render(request, 'dash/pqrs_admin.html', context)

@login_required
def responder_pqrs(request, id_pqr):
    """Procesa el cambio de estado y respuesta de una PQRS."""
    if request.method == 'POST':
        pqr = get_object_or_404(PQRS, id=id_pqr)
        pqr.respuesta = request.POST.get('respuesta')
        pqr.estado = request.POST.get('estado')

        # Notificación automática al usuario si se resuelve
        if pqr.estado == 'Resuelto' and pqr.respuesta:
            subject = f"Respuesta a su solicitud - Radicado {pqr.radicado}"
            message = f"Hola {pqr.nombre},\n\nHemos dado respuesta a su {pqr.tipo}.\n\nRespuesta:\n{pqr.respuesta}\n\nPuede consultar el historial en: {settings.DOMAIN_NAME}/consultar-pqrs/?radicado={pqr.radicado}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [pqr.correo], fail_silently=True)
        
        pqr.save()
        messages.success(request, f"Radicado {pqr.radicado} actualizado correctamente.")
    return redirect('gestion_pqrs')

@login_required
def gestion_cotizaciones(request):
    """Vista para que el Administrador gestione todas las solicitudes de cotización."""
    usuario_logeado_id = request.session.get('usuario_logeado')
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
    
    # Verificación de Rol Administrador (Seguridad)
    if not request.user.is_superuser:
        try:
            empleado = Empleado.objects.get(id=usuario_profile.id)
            if not (empleado.id_rol and empleado.id_rol.nombre == "Administrador"):
                messages.error(request, "No tienes permisos para este módulo.")
                return redirect('index')
        except Empleado.DoesNotExist:
            return redirect('index')

    cotizaciones_qs = Cotizacion.objects.all().order_by('-fecha_creacion')
    
    p = Paginator(cotizaciones_qs, 15) # 15 por página
    pagina = p.get_page(request.GET.get('page'))

    context = {
        'cotizaciones_list': pagina,
        'usuario': usuario_profile,
        'nombre_rol': "Administrador",
        'usuarios': 1,
        'total_cotizaciones': cotizaciones_qs.count(),
    }
    return render(request, 'dash/cotizaciones_admin.html', context)
