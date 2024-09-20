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
from paginaPetrocentro.models import Usuario,Estado
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
import uuid
from django.utils.text import slugify
from django.core.mail import send_mail


# Create your views here.
def obtener_permisos(permisos):
    
    crear = 0
    eliminar = 0
    editar = 0
    consultar = 0
    usuarios = 0 
   
    for permiso in permisos:
        if permiso.permiso.nombre == "Crear":
            crear = 1
    for permiso in permisos:
        if permiso.permiso.nombre == "Consultar":
            consultar = 1
    for permiso in permisos: 
        if permiso.permiso.nombre == "Eliminar":
            eliminar = 1
    for permiso in permisos:
        if permiso.permiso.nombre == "Actualizar":
            editar = 1 
    for permiso in permisos:
        if permiso.permiso.nombre == "Usuarios":
            usuarios = 1
    data={
        'crear':crear,
        'consultar': consultar,
        'editar': editar,
        'eliminar': eliminar,
        'usuarios': usuarios,
    }
    return data

# Create your views here.
@login_required
def perfil(request):
    
        usuario_logeado = request.session.get('usuario_logeado') #Obtener el id del user logeado

        
        try:
                emp = Usuario.objects.get(id = usuario_logeado )
                emplea= Empleado.objects.get(id = emp.id)
                rol = emplea.id_rol
                nombre_rol = rol.nombre
                empleado = Empleado.objects.get(id = emp.id) 
                permisos = Rol_permiso.objects.filter(rol = rol)
                obtener_permiso = obtener_permisos(permisos)
            

                
                #Enviamos toda la data al template 
                data = {
                'usuario': emp,
                'empleado': empleado,
                'crear': obtener_permiso['crear'],
                'usuarios':obtener_permiso['usuarios'],
                'editar': obtener_permiso['editar'],
                'eliminar': obtener_permiso['eliminar'],
                'nombre_rol' : nombre_rol,
                }
                return render(request, 'configuracion/perfil.html', data)


        except Usuario.DoesNotExist as e :
                usuario = Usuario.objects.get(id = usuario_logeado)
                data = {'usuario': usuario}
                return render(request, 'configuracion/perfil.html', data)

def editar_perfil(request):
    if request.method == 'POST':
       
        usuario_logeado = request.session.get('usuario_logeado')
        usuario = Usuario.objects.get(id = usuario_logeado)
        nombre = request.POST.get('nombre')
        identificacion = request.POST.get('identificacion')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        foto= request.FILES.get('foto')
         
         
        if foto:
            usuario.foto_perfil=foto
            usuario.nombre=nombre
            usuario.identificacion=identificacion
            usuario.correo=correo
            usuario.telefono = telefono

            usuario.save()
        else:
            usuario.nombre=nombre
            usuario.identificacion=identificacion
            usuario.correo=correo
            usuario.telefono = telefono
            usuario.save()
            
        if usuario:
            messages.success(request, 'Perfil modificado exitosamente')
            return redirect('perfil')
        else:
            messages.error(request, 'No se pudo modificar el usuario')

        return redirect('perfil')
    
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

@login_required
def configuracion_nosotros (request):
    usuario_logeado = request.session.get('usuario_logeado')
    try:  
        emp = Usuario.objects.get(id = usuario_logeado )
        emplea= Empleado.objects.get(id = emp.id)
        rol = emplea.id_rol
        nombre_rol = rol.nombre
        empleado = Empleado.objects.get(id = emp.id) 
        permisos = Rol_permiso.objects.filter(rol_id = rol)
        obtener_permiso = obtener_permisos(permisos)

        
            
        fotos=Nosotros.objects.all()
        data={
        'fotos': fotos,
        'empleado': empleado,
        'nombre_rol':nombre_rol,
        'usuario': emp,
        'crear': obtener_permiso['crear'],
        'usuarios':obtener_permiso['usuarios'],
        'editar': obtener_permiso['editar'],
        'eliminar': obtener_permiso['eliminar'],
        'empleado': empleado,
        }

        return render(request, 'configuracion/nosotros_conf.html',data)
    except Exception as e:
        messages.error(request, f'Error : {e}')
        return redirect('inicio')

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
@login_required
def roles(request):
    usuario_logeado = request.session.get('usuario_logeado')
    try:
        emp = Usuario.objects.get(id = usuario_logeado )
        emplea= Empleado.objects.get(id = emp.id)
        rol = emplea.id_rol
        nombre_rol = rol.nombre
        empleado = Empleado.objects.get(id = emp.id) 
        permisos = Rol_permiso.objects.filter(rol = rol)
        obtener_permiso = obtener_permisos(permisos)

  
            
        if nombre_rol == "Administrador" and emplea.estado.id == 1:   
            rol_permiso= Rol_permiso.objects.all()
            permiso = Rol.objects.all()
            rol= Rol.objects.all()
            
            data = {
                
                'empleado':empleado,
                'roles': rol,
                'permisos':permiso,
                'rol_permisos': rol_permiso,
                'crear': obtener_permiso['crear'],
                'editar': obtener_permiso['editar'],
                'usuarios': obtener_permiso['usuarios'],
                'eliminar': obtener_permiso['eliminar'],
                'empleado': empleado,
                'nombre_rol':nombre_rol,
                'usuario': emp,
                
            }
            return render(request,'configuracion/roles.html', data)
        else:
            messages.error(request, 'No tiene permisos para este modulo')
            return redirect('empleados')
            
       
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('empleados')
    
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
                messages.success(request, 'Rol creado correctamente.')
                return redirect('asignar_roles')

            
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('asignar_roles')


def agregar_permisos(request,id):
    if request.method == 'POST':
        try:
            crear = request.POST.get('crear')
            consultar = request.POST.get('consultar')
            editar = request.POST.get('editar')
            eliminar = request.POST.get('eliminar')
            proyecto = request.POST.get('proyecto')
            usuarios = request.POST.get('usuarios')
  
                     
            rol = Rol.objects.get(id_rol=id)

            #Crear
            if crear == 'on':                
                permiso = Permisos.objects.get(nombre="Crear")
                if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                    Rol_permiso.objects.create(rol = rol, permiso = permiso)
            else:
                permiso = Permisos.objects.get(nombre="Crear")                
                Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                
            #Eliminar
            if eliminar == 'on':
                permiso = Permisos.objects.get(nombre="eliminar")                
                if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                    Rol_permiso.objects.create(rol = rol, permiso = permiso)
            else:
                permiso = Permisos.objects.get(nombre="eliminar")                
                Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                
            #Editar    
            if editar == 'on':
                permiso = Permisos.objects.get(nombre="actualizar")                
                if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                    Rol_permiso.objects.create(rol = rol, permiso = permiso)
            else:
                permiso = Permisos.objects.get(nombre="actualizar")            
                Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                
            #Consultar
            if consultar == 'on':
                permiso = Permisos.objects.get(nombre="consultar")                
                if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                    Rol_permiso.objects.create(rol = rol, permiso = permiso)
            else:
                permiso = Permisos.objects.get(nombre="consultar")                
                Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()

            #Proyecto
     
          
                
            #Usuarios
            if usuarios == 'on':
                permiso = Permisos.objects.get(nombre="Usuarios")                
                if not Rol_permiso.objects.filter(rol = rol, permiso = permiso).exists():
                    Rol_permiso.objects.create(rol = rol, permiso = permiso)
            else:
                permiso = Permisos.objects.get(nombre="Usuarios")                
                Rol_permiso.objects.filter(rol = rol, permiso = permiso).delete()
                
            messages.success(request, 'Asignación de roles realizada.')
            return redirect('asignar_roles')
            
        except Exception as e:
            
            messages.error(request, f'Error: {e}')
            return redirect('asignar_roles')
        
    return redirect('asignar_roles')
        
#---------------------------------------------------------------- POSTS ----------------------------------------------------------------
def send_email_post(email,creador,fecha,post,titulo):
    
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
        usuario_logeado = request.session.get('usuario_logeado')
        try:
                emp = Usuario.objects.get(id = usuario_logeado )
                emplea= Empleado.objects.get(id = emp.id)
                rol = emplea.id_rol
                nombre_rol = rol.nombre
                empleado = Empleado.objects.get(id = emp.id) 
                permisos = Rol_permiso.objects.filter(rol = rol)
                obtener_permiso = obtener_permisos(permisos)
                post = Post.objects.order_by('-fecha_creacion')
        
                
                if nombre_rol == "Administrador" and emplea.estado.id == 1:   
                        rol_permiso= Rol_permiso.objects.all()
                        permiso = Rol.objects.all()
                        rol= Rol.objects.all()
                        
                        data = {
                                'posts':post,
                                'empleado':empleado,
                                'roles': rol,
                                'permisos':permiso,
                                'rol_permisos': rol_permiso,
                                'crear': obtener_permiso['crear'],
                                'editar': obtener_permiso['editar'],
                                'usuarios': obtener_permiso['usuarios'],
                                'eliminar': obtener_permiso['eliminar'],
                                'empleado': empleado,
                                'nombre_rol':nombre_rol,
                                'usuario': emp,
                                
                        }
                        return render(request,'configuracion/post_view.html', data)
                else:
                        messages.error(request, 'No tiene permisos para este modulo')
                        return redirect('empleados')
                
        except Exception as e:
                messages.error(request, f'Error: {e}')
                return redirect('empleados')

def crear_post(request):
        usuario_logeado = request.session.get('usuario_logeado')
        emp = Usuario.objects.get(id = usuario_logeado )
        emplea= Empleado.objects.get(id = emp.id)
        rol = emplea.id_rol
        nombre_rol = rol.nombre
        empleado = Empleado.objects.get(id = emp.id) 
        permisos = Rol_permiso.objects.filter(rol = rol)
        obtener_permiso = obtener_permisos(permisos)
        try:
            
                form = Form_post()
                
                data={ 
                    'form': form,
                    'empleado':empleado,
                    'crear': obtener_permiso['crear'],
                    'editar': obtener_permiso['editar'],
                    'usuarios': obtener_permiso['usuarios'],
                    'eliminar': obtener_permiso['eliminar'],
                    'empleado': empleado,
                    'nombre_rol':nombre_rol,
                    'usuario': emp,
                      }
                    
                
                return render(request, 'configuracion/crear_post.html',data)
        except Exception as e:
                messages.error(request, f'Error: {e}')
                return redirect('crear_post')

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
                            full_url = f"{settings.DOMAIN_NAME}{url}"
                            if empleado == True:
                                empleados = Empleado.objects.all()
                                for empleado in empleados:
                                    send_email_post(empleado.correo, creador.nombre, post.fecha_creacion,full_url, titulo )
                            else:
                                
                                suscriptores = Suscriptores.objects.all()
                                for suscriptor in suscriptores:
                                    send_email_post(suscriptor.correo, creador.nombre, post.fecha_creacion,full_url,titulo )
                            return redirect('blog')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('crear_post')
                        

def editar_post_view(request, slug):

    post = get_object_or_404(Post, slug = slug)
    usuario_logeado = request.session.get('usuario_logeado')
    emp = Usuario.objects.get(id = usuario_logeado )
    emplea= Empleado.objects.get(id = emp.id)
    rol = emplea.id_rol
    nombre_rol = rol.nombre
    empleado = Empleado.objects.get(id = emp.id) 
    permisos = Rol_permiso.objects.filter(rol = rol)
    obtener_permiso = obtener_permisos(permisos)
    if request.method == 'POST':
        form = Form_post(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('crear_post_view')
    else:
        form = Form_post(instance=post)

    data={
        'form': form,
        'post': post,
        'empleado':empleado,
        'crear': obtener_permiso['crear'],
        'editar': obtener_permiso['editar'],
        'usuarios': obtener_permiso['usuarios'],
        'eliminar': obtener_permiso['eliminar'],
        'empleado': empleado,
        'nombre_rol':nombre_rol,
        'usuario': emp,
        }
    return render(request, 'configuracion/editar_post_view.html', data)

