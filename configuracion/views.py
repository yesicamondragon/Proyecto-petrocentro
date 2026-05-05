from django.shortcuts import get_object_or_404, render
import json
from django.shortcuts import redirect, render
# Create your views here.
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import os

from django.urls import reverse
from blogs.forms import Form_post
from users.models import *
from .models import *
from Petrocentro import settings
from blogs.models import *
from django.contrib.auth.models import User
from paginaPetrocentro.models import Usuario, Estado, Suscriptores
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
import uuid
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.core.mail import send_mail


# Create your views here.
def obtener_permisos(permisos):
    
    crear = 0
    eliminar = 0
    editar = 0
    consultar = 0
    usuarios = 0 
   
    for permiso in permisos:
        nombre = permiso.permiso.nombre
        if nombre == "Crear":
            crear = 1
        elif nombre in ["Consultar", "Consultor"]:
            consultar = 1
        elif nombre == "Eliminar":
            eliminar = 1
        elif nombre in ["Actualizar", "Editar", "Editor"]:
            editar = 1 
        elif nombre == "Usuarios":
            usuarios = 1
    data={
        'crear':crear,
        'consultar': consultar,
        'editar': editar,
        'eliminar': eliminar,
        'usuarios': usuarios,
    }
    return data


# -----------------------------------------------------------------------PERFIL-------------
#Funcion que redirige a la vista del perfil.
@login_required
def perfil(request):
    usuario_logeado_id = request.session.get('usuario_logeado')

    if not usuario_logeado_id:
        messages.error(request, "Tu sesión ha expirado. Por favor, inicia sesión de nuevo.")
        return redirect('login_view')

    # Todos los usuarios logueados deben tener un perfil de Usuario.
    usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)

    # Inicializamos el contexto con la información base y permisos por defecto.
    context = {
        'usuario': usuario_profile,
        'empleado': None,
        'nombre_rol': 'Usuario',
        'crear': 0,
        'usuarios': 0,
        'editar': 0,
        'eliminar': 0,
    }

    # Ahora, intentamos obtener el perfil de Empleado y sus permisos.
    try:
        empleado_profile = Empleado.objects.get(id=usuario_profile.id)
        context['empleado'] = empleado_profile
        
        rol = empleado_profile.id_rol
        if rol:
            context['nombre_rol'] = rol.nombre
            permisos_qs = Rol_permiso.objects.filter(rol=rol)
            permisos_data = obtener_permisos(permisos_qs)
            context.update(permisos_data) # Actualiza el contexto con los permisos
        else:
            context['nombre_rol'] = "Empleado (Sin Rol)"

    except Empleado.DoesNotExist:
        # Es un usuario normal sin perfil de empleado, el contexto base es suficiente.
        pass

    # Si es superusuario, sobreescribimos los permisos para darle acceso total.
    if request.user.is_superuser:
        context['nombre_rol'] = "Administrador"
        context.update({'crear': 1, 'consultar': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1})

    return render(request, 'configuracion/perfil.html', context)

#Funcion que edita si es preciso los campos del perfil.
def editar_perfil(request):
    if request.method == 'POST':
       
        usuario_logeado_id = request.session.get('usuario_logeado')
        usuario = get_object_or_404(Usuario, id=usuario_logeado_id)
        
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        foto= request.FILES.get('foto')
         
        # Actualizar datos básicos de Usuario (Perfil Personal)
        usuario.nombre = nombre
        usuario.correo = correo
        if foto:
            # Eliminar la foto anterior si existe para no acumular archivos basura
            if usuario.foto_perfil:
                usuario.foto_perfil.delete(save=False)
            usuario.foto_perfil = foto
        usuario.save()

        # Actualizar datos extendidos de Empleado (Teléfono, Identificación) si existen
        identificacion = request.POST.get('identificacion')
        telefono = request.POST.get('telefono')
        
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            empleado.identificacion = identificacion
            empleado.telefono = telefono
            empleado.save()
        except Empleado.DoesNotExist:
            pass

        if usuario:
            messages.success(request, 'Perfil modificado exitosamente')
            return redirect('perfil')
        else:
            messages.error(request, 'No se pudo modificar el usuario')

        return redirect('perfil')
    
#Función que permite eliminar la foto de perfil.
def delete_photo(request):
   
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ruta = data.get('ruta_relativa')
            
            file_path = os.path.join(settings.MEDIA_ROOT,ruta.lstrip('/'))
            
            print(file_path)
            usuario_logeado = request.session.get('usuario_logeado')
            usuario_logeado = Usuario.objects.get(id = usuario_logeado)
            
            if os.path.exists(file_path):
                print(file_path)
                os.remove(file_path)
                usuario_logeado.foto_perfil.delete()
                usuario_logeado.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Archivo no encontrado'})
        except Exception as e:
            print(file_path)
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

#Función para cambiar la contraseña.
def password_change(request, id):
    
    if request.method == 'POST':
        usuario = Usuario.objects.get(id = id)
        user = User.objects.get(username = usuario.user_id.username)
        password=user.password
        print('la contraseña es',password)
  
        newPasword1 = request.POST.get('new-password1')
        newPasword2 = request.POST.get('new-password2')
        if newPasword1 == newPasword2:
            newPasword1 = make_password(newPasword1)
            user.password = newPasword1
            update_session_auth_hash(request, user)
            user.save()
            if user:
                messages.success(request, 'Contraseña cambiada exitosamente.')
                return redirect('perfil')    
        else:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('password_change', id=id)
  
    else:
        messages.error(request, 'Por favor corrija los errores en el formulario.')
    return redirect('perfil')

#------------------------------------------------------------COFIGURACION ----------------------------------------------------------------

#Funcion que dirige a la vista de configuracion de las fotos del carrusel en la pagina "nosotros".
@login_required
def configuracion_nosotros (request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado = Empleado.objects.get(id=emp.id)
        except Empleado.DoesNotExist:
            pass # Superuser might not be an employee
    else:
        try:
            empleado = Empleado.objects.get(id=emp.id)
            if empleado.id_rol and empleado.id_rol.nombre == "Administrador":
                nombre_rol = "Administrador"
                permisos_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                messages.error(request, 'No tienes permisos para acceder a la configuración.')
                return redirect('index')
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # --- Lógica de la vista ---
    fotos = Nosotros.objects.all()
    data = {
        'fotos': fotos, 'empleado': empleado, 'nombre_rol': nombre_rol, 'usuario': emp,
        'crear': permisos.get('crear', 0), 'usuarios': permisos.get('usuarios', 0),
        'editar': permisos.get('editar', 0), 'eliminar': permisos.get('eliminar', 0),
    }
    return render(request, 'configuracion/nosotros_conf.html', data)

#Funcion que permite agregar las fotos al carrusel.
def agregar_fotos_nosotros(request):
    if request.method == 'POST':
        
        try:
                fotos_nosotros = request.FILES.get('agregar')
                descripcion =  request.POST.get('descripcion')
                if fotos_nosotros: 
                    nosotros = Nosotros(descripcion=descripcion, foto=fotos_nosotros)
                    nosotros.save()
                    if nosotros:
                        messages.success(request, 'Foto agregada correctamente.')
                        return redirect('nosotros_conf')
                else:
                    messages.error(request, 'Debe seleccionar una imagen.')
                    return redirect('nosotros_conf')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('nosotros_conf')

#Funcion que permite eliminar la foto, simplemente la foto.
def eliminar_foto_nosotros(request):
     if request.method == "POST":
        try:
                
                data = json.loads(request.body) #Realizar la obtención de lo que trae el Json enviado desde el template
                ruta = data.get('ruta_relativa') #Del Json, recibir la ruta de la imagen
                id = data.get('id_foto') #Del Json recibir el id del insumo
                print('el id es: ',id)
                print('la ruta es: ',ruta)
                
                foto = Nosotros.objects.get(id=id) #Se realiza la instancia del objeto 
                
                file_path = os.path.join(settings.MEDIA_ROOT,ruta.lstrip('/')) #Se busca la imagen en el proyecto
                if os.path.exists(file_path):
                    os.remove(file_path) #Se elimina el archivo
                    foto.delete() #Se elimina el objeto en la base de datos
                    messages.success(request, 'Foto eliminada correctamente.')
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'La imagen no existe en el proyecto.'})                
                
            
        except Exception as e:
        
            return JsonResponse({'status': 'error', 'message': str(e)})
 
 #Funcion que permite eliminar todo el campo de la base de datos. Foto, descripcion; todo.

#Funcion que permite eliminar el campo completo 
def delete_photo_nosotros(request):
     if request.method == "POST":
        try:
                
                data = json.loads(request.body) #Realizar la obtención de lo que trae el Json enviado desde el template
                ruta = data.get('ruta_relativa') #Del Json, recibir la ruta de la imagen
                id = data.get('id_foto') #Del Json recibir el id del insumo

                print('la ruta es: ',ruta)
                
                foto = Nosotros.objects.get(id=id) #Se realiza la instancia del objeto 
                
                file_path = os.path.join(settings.MEDIA_ROOT,ruta.lstrip('/')) #Se busca la imagen en el proyecto
                if os.path.exists(file_path):
                    os.remove(file_path) #Se elimina el archivo
                    foto.foto.delete()
                    foto.save()
                    messages.success(request, 'Foto eliminada correctamente.')
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'La imagen no existe en el proyecto.'})                
                
            
        except Exception as e:
        
            return JsonResponse({'status': 'error', 'message': str(e)})
 
 #Funcion que permite editar los datos de la imagen
def editar_nosotros(request,id):
    if request.method == 'POST':
        try:
            foto = request.FILES.get('foto')
            descripcion = request.POST.get('descripcion')
            nosotros = Nosotros.objects.get(id=id)
     
            if foto:
                nosotros.descripcion = descripcion
                nosotros.foto = foto
                nosotros.save()
                
                if nosotros:
                    messages.success(request, 'Foto editada correctamente.')
                return redirect('nosotros_conf')
            else:
                nosotros.descripcion = descripcion
                nosotros.save()
                
                if nosotros:
                    messages.success(request, 'Descripcion editada correctamente.')
                return redirect('nosotros_conf')
            
 
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('nosotros_conf')
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
   
   
#---------------------------------------------------------------- ROLES Y PERMISOS ----------------------------------------------------------------

#Funcion que dirige a la vista de los roles.
@login_required
def roles(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado = Empleado.objects.get(id=emp.id)
        except Empleado.DoesNotExist:
            pass # Superuser might not be an employee
    else:
        try:
            empleado = Empleado.objects.get(id=emp.id)
            if empleado.id_rol and empleado.id_rol.nombre == "Administrador":
                nombre_rol = "Administrador"
                permisos_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                messages.error(request, 'No tienes permisos para este módulo.')
                return redirect('index')
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # --- Lógica de la vista ---
    lista_empleados_qs = Empleado.objects.select_related('id_rol', 'id_cargo', 'id_ubicacion').all().order_by('nombre')
    
    p = Paginator(lista_empleados_qs, 10) # Paginar, por ejemplo, 10 empleados por página
    page_number = request.GET.get('page')
    pagina_empleados = p.get_page(page_number)

    data = {
        'empleado': empleado, 'roles': Rol.objects.prefetch_related('permiso').all(),
        'permisos': Permisos.objects.all(), 'rol_permisos': Rol_permiso.objects.all(),
        'crear': permisos.get('crear', 0), 'editar': permisos.get('editar', 0),
        'usuarios': permisos.get('usuarios', 0), 'eliminar': permisos.get('eliminar', 0),
        'lista_empleados': pagina_empleados, # Usar la lista paginada
        'paginator_empleados': p, # Pasar el objeto Paginator para controles en el template
        'nombre_rol': nombre_rol, 'usuario': emp,
    }
    return render(request, 'configuracion/roles.html', data)
    
#Funcion que filtra los roles desde la plantilla, esta funcion se llama mediante javascript.
def filtrar_permisos(request):
    try:
        data = json.loads(request.body)
        rol = data.get('rol')
        permiso = Rol_permiso.objects.filter(rol_id = rol)
        permisos = obtener_permisos(permiso)
        
        
        data={
            
            'crear':permisos['crear'],
            'consultar': permisos['consultar'],
            'editar': permisos['editar'],
            'eliminar': permisos['eliminar'],
            'usuarios': permisos['usuarios'],
       
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
#Funcion que permite crear un nuevo rol.
@login_required
def crear_rol(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            
            rol_existe = Rol.objects.filter(nombre=nombre).exists()
            
            if rol_existe:
                messages.error(request, 'El nombre del rol ya existe.')
                return redirect('asignar_roles')
            elif nombre == '':
                messages.error(request, 'El nombre del rol no puede estar vacío.')
                return redirect('asignar_roles')
            else:
                
                rol = Rol(nombre=nombre)
                rol.save()
                
                # Historial de cambios
                try:
                    admin = Usuario.objects.get(id=request.session.get('usuario_logeado'))
                    LogActividad.objects.create(
                        admin_responsable=admin,
                        accion="Crear Rol",
                        detalles=f"Se creó el rol: {nombre}"
                    )
                except: pass

                messages.success(request, 'Rol creado correctamente.')
                return redirect('asignar_roles')

            
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('asignar_roles')

#Funcion que permite agregar permisos a un rol.
def agregar_permisos(request,id):
    if request.method == 'POST':
        try:
            # Gestión Granular: Se mapea el input del form con el nombre en BD
            # Esto permite activar/desactivar permisos específicos
            crear = request.POST.get('crear')
            consultar = request.POST.get('consultar')
            editar = request.POST.get('editar')
            eliminar = request.POST.get('eliminar')
            usuarios = request.POST.get('usuarios')
  
            rol = Rol.objects.get(id_rol=id)
            cambios_realizados = []

            # Helper para buscar permisos con variantes de nombre (evita error DoesNotExist)
            def get_permiso_seguro(lista_nombres):
                return Permisos.objects.filter(nombre__in=lista_nombres).first()

            #Crear
            permiso = get_permiso_seguro(["Crear"])
            if permiso:
                if crear == 'on':                
                    if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.create(rol = rol, permiso = permiso)
                        cambios_realizados.append("Activar Crear")
                else:
                    if Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                        cambios_realizados.append("Desactivar Crear")
                
            #Eliminar
            permiso = get_permiso_seguro(["Eliminar"])
            if permiso:
                if eliminar == 'on':
                    if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.create(rol = rol, permiso = permiso)
                        cambios_realizados.append("Activar Eliminar")
                else:
                    if Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                        cambios_realizados.append("Desactivar Eliminar")
                
            #Editar    
            permiso = get_permiso_seguro(["Editar", "Editor", "Actualizar"])
            if permiso:
                if editar == 'on':
                    if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.create(rol = rol, permiso = permiso)
                        cambios_realizados.append("Activar Editar")
                else:
                    if Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                        cambios_realizados.append("Desactivar Editar")
                
            #Consultar
            permiso = get_permiso_seguro(["Consultar", "Consultor"])
            if permiso:
                if consultar == 'on':
                    if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.create(rol = rol, permiso = permiso)
                        cambios_realizados.append("Activar Consultar")
                else:
                    if Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                        cambios_realizados.append("Desactivar Consultar")
                
            #Usuarios
            permiso = get_permiso_seguro(["Usuarios"])
            if permiso:
                if usuarios == 'on':
                    if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.create(rol = rol, permiso = permiso)
                        cambios_realizados.append("Activar Usuarios")
                else:
                    if Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                        Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                        cambios_realizados.append("Desactivar Usuarios")
            
            # Historial de cambios en roles
            if cambios_realizados:
                try:
                    admin = Usuario.objects.get(id=request.session.get('usuario_logeado'))
                    LogActividad.objects.create(
                        admin_responsable=admin,
                        accion="Modificar Permisos Rol",
                        detalles=f"Rol {rol.nombre}: {', '.join(cambios_realizados)}"
                    )
                except: pass
                
            messages.success(request, 'Asignación de roles realizada.')
            return redirect('asignar_roles')
            
        except Exception as e:
            
            messages.error(request, f'Error: {e}')
            return redirect('asignar_roles')
        
    return redirect('asignar_roles')

@login_required
def asignar_usuarios_rol(request, id):
    """Asigna masivamente usuarios a un rol específico desde la vista de roles."""
    if request.method == 'POST':
        try:
            rol = get_object_or_404(Rol, id_rol=id)
            usuarios_ids = request.POST.getlist('usuarios_seleccionados')
            
            if not usuarios_ids:
                messages.warning(request, "No seleccionaste ningún usuario.")
                return redirect('asignar_roles')

            # Actualizar empleados
            empleados_afectados = Empleado.objects.filter(id__in=usuarios_ids)
            count = empleados_afectados.update(id_rol=rol)

            # Historial
            try:
                admin = Usuario.objects.get(id=request.session.get('usuario_logeado'))
                LogActividad.objects.create(
                    admin_responsable=admin,
                    accion="Asignación Masiva Rol",
                    detalles=f"Se asignó el rol '{rol.nombre}' a {count} usuarios."
                )
            except: pass

            messages.success(request, f"Se asignó el rol {rol.nombre} a {count} empleados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al asignar usuarios: {e}")
    
    return redirect('asignar_roles')
        
@login_required
def eliminar_rol(request, id):
    # Verificación de permisos
    usuario_logeado_id = request.session.get('usuario_logeado')
    try:
        emp = Empleado.objects.get(id=usuario_logeado_id)
        permiso_eliminar = False
        
        if request.user.is_superuser:
            permiso_eliminar = True
        elif emp.id_rol:
            # Verificar si tiene permiso 'Eliminar' en su rol
            permiso_eliminar = Rol_permiso.objects.filter(rol=emp.id_rol, permiso__nombre='Eliminar').exists()
            
        if not permiso_eliminar:
            messages.error(request, 'No tienes permisos para eliminar roles.')
            return redirect('asignar_roles')

        rol = get_object_or_404(Rol, id_rol=id)

        # Protección para roles del sistema
        # Evitamos borrar roles críticos
        if rol.nombre in ['Administrador', 'Empleado']:
            messages.error(request, f'El rol "{rol.nombre}" es fundamental para el sistema y no puede ser eliminado.')
            return redirect('asignar_roles')

        rol.delete()
        
        # Log de actividad (Opcional, si deseas registrar la acción)
        messages.success(request, 'Rol eliminado correctamente.')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar el rol: {e}')
    
    return redirect('asignar_roles')

#---------------------------------------------------------------- POSTS ----------------------------------------------------------------

def send_email_post(email,creador,fecha,post,titulo):
    
        # Al estar en configuracion/templates/emails/, la ruta relativa es emails/...
        template = render_to_string('emails/email_blog_suscriptor.html',{
            'creador' : creador,
            'titulo':titulo,
            'fecha' : fecha,
            'post':post,
        })
        
        message = 'Nuevo Post!'
        
        from_email = settings.EMAIL_HOST_USER 
        
        to_email = [email]
        subject = 'Nuevo Post!'
        
        send_mail(subject,message ,  from_email, to_email, html_message=template)
        
def crear_post_view(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
        nombre_rol = "Administrador"
        try:
            empleado = Empleado.objects.get(id=emp.id)
        except Empleado.DoesNotExist:
            pass # Un superusuario podría no ser un empleado
    else:
        try:
            empleado = Empleado.objects.get(id=emp.id)
            if empleado.id_rol:
                rol_nom = empleado.id_rol.nombre
                nombre_rol = rol_nom
                permisos_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # --- Verificación de autorización ---
    is_active_employee = empleado and empleado.estado.id == 1
    can_view = nombre_rol in ["Administrador", "Empleado"] and (user.is_superuser or is_active_employee)

    if not can_view:
        messages.error(request, 'No tienes permisos para este módulo.')
        return redirect('index')

    # --- Lógica de la vista ---
    post = Post.objects.select_related('author', 'categoria').order_by('-fecha_creacion')
    data = {
        'posts': post, 'empleado': empleado, 'usuario': emp,
        'nombre_rol': nombre_rol, 'crear': permisos.get('crear', 0),
        'editar': permisos.get('editar', 0), 'usuarios': permisos.get('usuarios', 0),
        'eliminar': permisos.get('eliminar', 0),
    }
    return render(request, 'configuracion/post_view.html', data)

@login_required
def crear_post(request):
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
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
                permisos_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # --- Verificación de autorización para crear ---
    if not permisos.get('crear'):
        messages.error(request, 'No tienes permisos para crear posts.')
        return redirect('crear_post_view')

    # --- Lógica de la vista ---
    form = Form_post()
    data = {
        'form': form, 'empleado': empleado, 'usuario': emp,
        'nombre_rol': nombre_rol, 'crear': permisos.get('crear', 0),
        'editar': permisos.get('editar', 0), 'usuarios': permisos.get('usuarios', 0),
        'eliminar': permisos.get('eliminar', 0),
    }
    return render(request, 'configuracion/crear_post.html', data)

def guardar_post(request):
        usuario_logeado = request.session.get('usuario_logeado')
        usuario_logeado = Usuario.objects.get(id = usuario_logeado)
        try:
            if request.method == 'POST':
                    form = Form_post(request.POST, request.FILES)
                    
                    if form.is_valid():
                            cleaned_data = form.cleaned_data
                            titulo = cleaned_data.get('titulo')
                            descripcion = cleaned_data.get('descripcion')
                            contenido = cleaned_data.get('contenido')
                            image = cleaned_data.get('image')
                            categoria = cleaned_data.get('categoria')
                            empleado = cleaned_data.get('empleado')
                            slug = slugify(titulo)
                            original_slug = slug
                            queryset = Post.objects.filter(slug__startswith=slug)
                            if queryset.exists():
                                    while queryset.exists():
                                            slug = f"{original_slug}-{uuid.uuid4().hex[:8]}"
                                            queryset = Post.objects.filter(slug__startswith=slug)
                                            
                            post = Post(
                                    titulo=titulo, 
                                    descripcion=descripcion, 
                                    contenido=contenido, 
                                    empleado = empleado,
                                    image=image, 
                                    categoria= categoria,
                                    author = Usuario.objects.get(id =usuario_logeado.id ),
                                    slug=slug,
                                    
                            )
                            post.save()
                            creador = Usuario.objects.get(id =usuario_logeado.id )
                            url = reverse('detail-post', kwargs={'slug': post.slug})
                            full_url = f"{settings.DOMAIN_NAME.rstrip('/')}{url}"
                            if empleado == True:
                                empleados = Empleado.objects.all()
                                for empleado in empleados:
                                    try:
                                        send_email_post(empleado.correo, creador.nombre, post.fecha_creacion, full_url, titulo)
                                    except Exception as e:
                                        print(f"Error enviando a empleado {empleado.correo}: {e}")
                            else:
                                suscriptores = Suscriptores.objects.all()
                                if not suscriptores.exists():
                                    print("No hay suscriptores para notificar.")
                                    
                                for suscriptor in suscriptores:
                                    try:
                                        send_email_post(suscriptor.correo, creador.nombre, post.fecha_creacion, full_url, titulo)
                                    except Exception as e:
                                        print(f"Error enviando a suscriptor {suscriptor.correo}: {e}")
                                        
                            return redirect('blog')
                        
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('crear_post')
                        

@login_required
def editar_post_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    usuario_logeado_id = request.session.get('usuario_logeado')
    user = request.user

    # --- Obtener perfil de usuario y permisos ---
    permisos = {}
    emp = get_object_or_404(Usuario, id=usuario_logeado_id)
    empleado = None
    nombre_rol = "Usuario"

    if user.is_superuser:
        permisos = {'crear': 1, 'editar': 1, 'eliminar': 1, 'usuarios': 1}
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
                permisos_qs = Rol_permiso.objects.filter(rol=empleado.id_rol)
                permisos = obtener_permisos(permisos_qs)
            else:
                nombre_rol = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            messages.error(request, 'No tienes un perfil de empleado para acceder a esta página.')
            return redirect('index')

    # --- Verificación de autorización para editar ---
    if not permisos.get('editar'):
        messages.error(request, 'No tienes permisos para editar posts.')
        return redirect('crear_post_view')

    # --- Lógica de la vista ---
    if request.method == 'POST':
        form = Form_post(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f"Post '{post.titulo}' actualizado correctamente.")
            return redirect('crear_post_view')
    else:
        form = Form_post(instance=post)

    data = {
        'form': form, 'post': post, 'empleado': empleado, 'usuario': emp,
        'nombre_rol': nombre_rol, 'crear': permisos.get('crear', 0),
        'editar': permisos.get('editar', 0), 'usuarios': permisos.get('usuarios', 0),
        'eliminar': permisos.get('eliminar', 0),
    }
    return render(request, 'configuracion/editar_post_view.html', data)
