from pyexpat.errors import messages
from django.shortcuts import redirect, render

from paginaPetrocentro.models import *
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Q
from paginaPetrocentro.forms import RegisterForm
from configuracion.models import *
from configuracion.views import obtener_permisos
#------------------------------------------------------EMPELADOS Y USUARIOS----------------------------------------------
@login_required
def listar_empleados(request):
        usuario_logeado = request.session.get('usuario_logeado')


        emp = Usuario.objects.get(id = usuario_logeado )
        emplea= Empleado.objects.get(id = emp.id)
        rol = emplea.id_rol
        nombre_rol = rol.nombre
        permiso = Rol_permiso.objects.filter(rol = rol)
        
  
        #Permisos de rol --------------------------------
        permisos = obtener_permisos(permiso)
                
        #A partir de este permiso mostrará la página, si tiene acceso 
        for permiso in permisos:
                print(permiso)
        if permisos['usuarios']== 1:
            usuarios =1
            cargo = Cargo.objects.all()
            ubicacion = Ubicacion.objects.all()
            rol = Rol.objects.all() 
            user = Usuario.objects.filter(  )
            empleado= Empleado.objects.all()
        
            #----------------------------------------------------------------------------------------------------------------
            #obtener el dato para realizar el filtro
            busqueda = request.GET.get("buscar") 
            fecha = request.GET.get("fechaI")
            estado= request.GET.get("estado")


            #----------------------------------------------------------------------------------------------------------------
            #Generar filtros por medio de estados, fechas, nombres y demás datos 
            if estado :
                empleado = Empleado.objects.filter(
                    
                Q(estado = estado)
                ).distinct()
                
            if busqueda:
                
                empleado= Empleado.objects.filter(
                    Q(id__icontains = busqueda)|
                    Q(nombre__icontains = busqueda)|
                    Q(telefono__icontains= busqueda)|
                    Q(identificacion__icontains= busqueda)|
                    Q(correo__icontains = busqueda)|
                    Q(id_rol__nombre__icontains = busqueda)|
                    Q(id_cargo__nombre__icontains = busqueda)|
                    Q(id_ubicacion__nombre__icontains = busqueda)
                ).select_related('user_id', 'id_rol', 'id_cargo', 'id_ubicacion')
        
            if fecha: 
                empleado= Empleado.objects.filter(
                    Q(fecha_ingreso__icontains = fecha)
                
                ).distinct()

                  #----------------------------------------------------------------------------------------------------------------   
      
            p = Paginator(empleado, 5)
            page_number = request.GET.get('page')
            pagina= p.get_page(page_number)

                
            data ={
                'cargos': cargo,
                'ubicaciones': ubicacion,
                'roles': rol,
                'users':user,                    
                'paginas': pagina,
                'paginator': p,
                
                'empleados': empleado,
                'nombre_rol': nombre_rol,
                'usuario':emp,
                
                'crear':permisos['crear'],
                'consultar': permisos['consultar'],
                'editar': permisos['editar'],
                'eliminar': permisos['eliminar'],
                'usuarios': permisos['usuarios'],
             
                }
                
            return render(request,'dash/empleados.html',data)
        else:
                print( 'No tiene permisos para acceder a esta página')
                return redirect('empleados')

    #Obtener todos las tablas de la base de datos

@login_required
def editar_empleados(request, id):
    usuario_logeado = request.session.get('usuario_logeado')
    
    
    try:
            emp = Usuario.objects.get(id = usuario_logeado )
            Empleado.objects.get(id = emp.id)
  
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('/')              

    if request.method == 'POST':
        #consulta para obtener el empleado que coincida con el id que envia el botón de editar
        usuario = Empleado.objects.get(id=id)
        

        #----------------------------------------------------------------------------------------------------------------
        try:    
            #Variable para almacenar el cargo enviado en el formulario, ya que solo se permite editar el cargo
            id_cargo = request.POST.get('cargo')
            id_rol = request.POST.get('rol')

            #En la variable usuario, se obtiene el cargo y se realiza una consulta que trae el cargo de la tabla "CARGO" para validar coincidencias y asi mismo cambiarlo en el empleado
            usuario.id_cargo = Cargo.objects.get(id_cargo = id_cargo)
            usuario.id_rol = Rol.objects.get(id_rol = id_rol)
            #gurdar el cargo
            usuario.save()
            
            #si es exitoso el cambio, envía un mensaje de éxito.
            if(usuario):
                messages.success(request, 'Se ha editado exitosamente')
            
          
            #si no es exitoso, envía un mensaje de error
            else:
                messages.error(request, 'No se ha editado exitosamente')
                
        #excepciones para validar errores
        except (KeyError, ValueError) as e:
            messages.error(request, e)
            
    return redirect('empleados')

@login_required
def registrar_empleados(request):

    usuario_logeado = request.session.get('usuario_logeado')
        
        
    try:
            emp = Usuario.objects.get(id = usuario_logeado )
            Empleado.objects.get(id = emp.id)

    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('/')              

    if request.method == 'POST' and request != None:
        
        #----------------------------------------------------------------------------------------------------------------
        #try para pedirle que en caso que falle, arroje el error en un mensaje y no el error de django 
        try:
            #Obtener toda la informacion del dormulario de empleados
            fecha = request.POST.get("fechaIngreso")
            id_cargo = request.POST.get('cargo')
            id_rol= request.POST.get('rol')
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
            #instancia de empleado para crear el mismo
            empleado= Empleado(
            
                    id=user.id,  # Usar la clave primaria del usuario
                    user_id= User.objects.get(id=usuario_num),  #la clave de user_auth para el usuario
                    identificacion= user.identificacion,
                    estado=user.estado,
                    nombre=user.nombre,
                    correo=user.correo,
                    telefono=user.telefono,
                    fecha_ingreso=fecha,
                    id_cargo= Cargo.objects.get(id_cargo = id_cargo),
                    id_rol = Rol.objects.get(id_rol = id_rol ),
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
                messages.success(request, 'Se ha registrado exitosamente.')
                
        #excepción        
        except (User.DoesNotExist, Estado.DoesNotExist, Rol.DoesNotExist, Cargo.DoesNotExist, Ubicacion.DoesNotExist, ValueError) as e:
                messages.error(request, 'Error en el formulario, por favor diligéncialo bien')
     
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
        estado = Estado.objects.get(id = id_estado)
        
        #se agrega a el campo de estado en la base de datos 
        usuario.estado = estado
        
        #se guarda el estado del usuario en la base de datos
        usuario.save()
        
        if usuario:
            messages.success(request,'Estado cambiado correctamente')
        else:
            messages.error(request, 'No se ha cambiado el estado correctamente')
   
    #----------------------------------------------------------------------------------------------------------------
    else:
        if usuario.user_id.is_authenticated:
                messages.error(request, 'Tu cuenta ha sido deshabilitada!')
                logout(request)
        #generar una variable que es la que cambiara el estado        
        id_estado = 2
        
        #cambiar el estado de Id_estado con el registrado      
        estado = Estado.objects.get(id = id_estado)
        
        #se agrega a el campo de estado en la base de datos 
        usuario.estado = estado      
        #se guarda el estado del usuario en la base de datos 
        usuario.save()
        if usuario:
            messages.success(request,'Estado cambiado correctamente')
        else:
            messages.error(request, 'No se ha cambiado el estado correctamente')

    return redirect('empleados')

@login_required
def registrar_usuario(request):
    usuario_logeado = request.session.get('usuario_logeado')
    
    
    try:
            emp = Usuario.objects.get(id = usuario_logeado )
            emplea= Empleado.objects.get(id = emp.id)
            rol = emplea.id_rol
            nombre_rol = rol.nombre
            permiso = Rol_permiso.objects.filter(rol = rol)
            permisos = obtener_permisos(permiso)
            #Permisos de rol
         
                
            if permisos['usuarios'] == 1 and emplea.estado.id == 1:
                usuarios= 1
            #consulta que permite obtener todos los usuarios
                user = Usuario.objects.all()
                
                        #Búsqueda
                busqueda = request.GET.get('buscar')
                #Si la búsqueda no está vacía, filtramos los usuarios que coincidan con la búsqueda en el nombre, telefono, identificación y correo. Distinct()  es para que no se repitan los resultados en caso de que haya coincidencias en varias columnas.
                if busqueda:
                    user = Usuario.objects.filter(
                        Q(nombre__icontains = busqueda)|
                        Q(telefono__icontains= busqueda)|
                        Q(identificacion__icontains= busqueda)|
                        Q(correo__icontains = busqueda)
                        ).distinct()
            
                #----------------------------------------------------------------------------------------------------------------
                #obtener el formulario de registro de usuario 
                form= RegisterForm(request.POST or None)
            
                #----------------------------------------------------------------------------------------------------------------
                p = Paginator(user, 5) 
                page_number = request.GET.get('page')
                pagina= p.get_page(page_number)
            
                #----------------------------------------------------------------------------------------------------------------
                #formulario de registrar usuario desde la dash
                if request.method == 'POST' and form.is_valid():
                    #declarar variable para traer el nombre
                    username= form.cleaned_data.get('username')
                    
                    #----------------------------------------------------------------------------------------------------------------        
                    #condicional para validación de contraseñas. 
                    if form.cleaned_data.get('contraseña') != form.cleaned_data.get('confirmar_contraseña'):
                        #mensaje de alerta
                        messages.error(request, f'Contraseñas no coinciden, {username}')

                    #condicional para validar si el usuario ya existe en la base de datos
                    elif User.objects.filter(username=username).exists():
                        #mensaje de alerta
                        messages.error(request,'Usuario existente')
                        
                    #-si cumple con las normas(que no se encuentre la persona en la base de datos y las contraseñas coincidan )
                    else:
                        #declarar variable para traer el correo 
                    
                        #declarar variable de usuario para validar si el usuario se creo correctamente en la base de datos, teniendo en cuenta el metodo save() creado en la clase RegisterForm del archovo forms.py        
                        user = form.save()
                        user_id = user.id
                        identificacion = form.cleaned_data['identificacion']
                        estado = 1
                        nombre = form.cleaned_data['nombre_completo']
                        correo= form.cleaned_data['correo_electronico']
                        telefono=form.cleaned_data['telefono']
                        
                        #----------------------------------------------------------------------------------------------------------------        
                        usuario = Usuario(
                            user_id = User.objects.get(id=user_id),
                            identificacion = identificacion,
                            estado = Estado.objects.get(id=estado),
                            nombre = nombre,
                            correo = correo,
                            telefono =  telefono ,
                        
                        )
                        usuario.save()
                        
                        if usuario:
                            messages.success(request,'Registro Exitoso')
                
                #----------------------------------------------------------------------------------------------------------------

                data ={
                    'form': form,
                    'paginas': pagina,
                    'paginator':p,
                    'usuario':emp,            
                                                    
                   'crear':permisos['crear'],
                    'consultar': permisos['consultar'],
                    'editar': permisos['editar'],
                    'eliminar': permisos['eliminar'],
                    'usuarios': permisos['usuarios'],
                  
                    
                }
                return render(request,'dash/usuarios.html',data)       
            else:
                return redirect('/')
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('/')              


