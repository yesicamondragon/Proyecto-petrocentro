import json
from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages
import os

from django.urls import reverse_lazy
from Petrocentro import settings
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from paginaPetrocentro.models import Usuario,Estado
from django.template.loader import render_to_string
from datetime import datetime
import requests
from bs4 import BeautifulSoup 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

class CustomPasswordResetView(PasswordResetView):

    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    def form_valid(self, form):
            """
        Genera y envía el correo de restablecimiento de contraseña
        """
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': self.extra_email_context,
            }
            form.save(**opts)
            return super().form_valid(form)
   
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    
#Funcion para redirigir al index
def index(request):
    #todo: Obtener el usuario logeado
    
    url = "https://www.google.com/finance/quote/USD-COP"
    response = requests.get(url)
    response.raise_for_status()  # Verifica si la solicitud fue exitosa (código 200)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    price_element = soup.find("div", {"class": "YMlKec fxKbKc"})
    
    if price_element:
        # Extraer el texto (precio) del elemento
        price = price_element.text

    usuario_logeado = request.session.get('usuario_logeado')
    # ·Si el usuario no esta logeado, lo redirige al index sin sus datos
    if  not  usuario_logeado:
        data={
                'dolar': price,
                'usuario':usuario_logeado
            }
        return render(request,'paginas/index.html',data )
     
   # Si el usuairio está logeado, envia sus datos y lo redirige
    else:
        try:
            usuario_logeado = request.session.get('usuario_logeado')
            usuario_logeado = Usuario.objects.get(id = usuario_logeado)

            data={
                'dolar': price,
                'usuario':usuario_logeado
            }
            return render(request,'paginas/index.html', data)
        except Exception as e:
                return render(request,'paginas/index.html')
        
#Funcion para redirigir al nosotros
def nosotros(request):
    usuario_logeado = request.session.get('usuario_logeado')

    if  not  usuario_logeado:
       
        return render(request,'paginas/nosotros.html' )
    
# Si el usuairio está logeado, envia sus datos y lo redirige
    else:
        try:
            
       
            usuario_logeado = request.session.get('usuario_logeado')
            usuario_logeado = Usuario.objects.get(id = usuario_logeado)
            data={
                'nosotros':nosotros,
                'usuario':usuario_logeado
            }
            return render(request,'paginas/nosotros.html', data)
        except Exception as e:
                return render(request,'paginas/nosotros.html')

def politicas_nosotros(request):
    usuario_logeado = request.session.get('usuario_logeado')

    if  not  usuario_logeado:
       
        return render(request,'paginas/politicas.html' )
    
# Si el usuairio está logeado, envia sus datos y lo redirige
    else:
        try:
            usuario_logeado = request.session.get('usuario_logeado')
            usuario_logeado = Usuario.objects.get(id = usuario_logeado)

            data={
                'nosotros':nosotros,
                'usuario':usuario_logeado
            }
            return render(request,'paginas/politicas.html', data)
        except Exception as e:
                return render(request,'paginas/politicas.html')
    
#Funcion para redirigir al servicios
def servicios(request):
    usuario_logeado = request.session.get('usuario_logeado')
    
    if  not  usuario_logeado:
        return render(request,'paginas/servicios.html')
    else:
        try:
            usuario_logeado = request.session.get('usuario_logeado')
            usuario_logeado = Usuario.objects.get(id = usuario_logeado)

            data={
                'usuario':usuario_logeado
            }
            return render(request,'paginas/servicios.html', data)
        except Exception as e:
                return render(request,'paginas/servicios.html')
        

#Funcion para redirigir al contacto
def contacto(request):
    
        usuario_logeado = request.session.get('usuario_logeado')
    
        if  not  usuario_logeado:
            return render(request,'paginas/contacto.html')

        else:
                try:
                    usuario_logeado = request.session.get('usuario_logeado')
                    usuario_logeado = Usuario.objects.get(id = usuario_logeado)
                    data={
                        'usuario':usuario_logeado
                    }
                    return render(request,'paginas/contacto.html', data)
                except Exception as e:
                        return render(request,'paginas/contacto.html')
                        
            
    #Funcion para redirigir al pqrs

def pqrs(request):
        usuario_logeado = request.session.get('usuario_logeado')
        try:
                if  not  usuario_logeado:
                        return render(request,'paginas/PQRS.html')

                else:
      
                        usuario_logeado = request.session.get('usuario_logeado')
                        usuario_logeado = Usuario.objects.get(id = usuario_logeado)
                        data={
                        'usuario':usuario_logeado
                        }
                        return render(request,'paginas/PQRS.html', data)
                
        except Exception as e:
               return render(request,'paginas/PQRS.html')

        

#Funcion para redirigir al registro
def registro(request):
     
    #Traer el formulario de registro del arciho forms.py
    form= RegisterForm(request.POST or None)
    
    #Hacer la pregunta por medio del método post, además se pregunta si el formulario es válido 
    if request.method == 'POST' and form.is_valid():
        #declarar variable para traer el nombre
        username= form.cleaned_data.get('username')

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
            
            
            usuario = Usuario(
                user_id = User.objects.get(id=user_id),
                identificacion = identificacion,
                estado = Estado.objects.get(id=estado),
                nombre = nombre,
                correo = correo,
                telefono =  telefono ,
               
            )
            usuario.save()
            
            email= form.cleaned_data.get('correo_electronico')
            
            
            #Validar si la respuesta retornada por el método save(), es Verdadera 
            if user:
                
            #mensaje de alerta
                messages.success(request,'Registro Exitoso')
                
                #declaracion de variable en donde se encuentra el mensaje html que será enviado al correo
                mensaje_html = render_to_string( 'plantillas/registro.html',{
                    'user': nombre,
                    'fecha': datetime.now(),
                    
                } )
                
                #declaracion de variable para el asunto
                subject = 'Registro exitoso'
                
                #declaracion de variable para el mensaje              
                message = '¡Gracias por registrarte en nuestro sitio!'
                
                #declaracion de variable que indica desde cual correo se generará el envio de correo
                from_email = settings.EMAIL_HOST_USER
                
                #declaracion de variable que indica la direccion de corero elecrtónico a la cuál será enviado el correo
                to_email = [email]
                
                #envio de correo, con las variables anteriormetne mencionadas
                send_mail(subject, message, from_email, to_email, html_message=mensaje_html)
            
                #generar la redirección
                return redirect('login_view')
                 
    return render(request,'registration/registro.html',{
        'form': form
    })

#Funcion de inicio de sesión
def login_view(request):
    
    #Hacer la pregunta por medio del método post, además se pregunta si el formulario es válido 
    if request.method == 'POST':

        #Declarar variable para guardar el nombre del usuario.
        username = request.POST.get('username')
  
        #declarar la variable para guardar la contraseña.
        password = request.POST.get('password')
        
        #declarar variable de usuario, donde valida si el usuario y la contraseña son correctos
        user = authenticate(username = username, password = password)
        
        #validar si la respuesta obtenida por la variable user es verdadera
        if user:
            
            usuario1 = User.objects.get(username=username)
            
            validacion = usuario1.id
            try:    
                usuario = Usuario.objects.get(user_id= validacion)
                
            except :
                messages.error(request, 'No se encontró al usuario')
                return redirect('login_view')

            if usuario.estado.id == 1:
                #creacion de la sesión
                login(request, user)                
                #mensaje de alerta
                messages.success(request,'Bienvenido {}'.format(usuario.nombre))                
                #redireccion al index, más adelante será la redireccion a donde su rol se lo permita
                try:                    
                        request.session['usuario_logeado']= usuario.id
                        return redirect('principal')
                
                except Exception as e:
                        request.session['usuario_logeado'] = usuario.id
                        return redirect('/')
            else:
                messages.error(request,'Tienes deshabilitada la cuenta {}'.format(user.username))
                
        #la respuesta obtenida por la variable "user" es falsa
        else:
            
            #mensaje de alerta
            messages.error(request,'Usuario o contrseña inválidos')
        
    return render(request,'registration/login.html',{
            
        })
    
#Funcion de cierre de sesión
def logout_view(request):
    
    #Cierre de la Sesión
    logout(request)
    
    #Mensaje de alerta
    messages.success(request,'Sesión cerrada correctamente')
    
    #Redirecion a la vista inicio de sesión 
    return redirect('/')


def contacto_mensaje(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('numero')
        mensaje = request.POST.get('mensaje')
        fecha = datetime.now()
        
        template = render_to_string('plantillas/email_contacto.html',{
            'nombre': 'Ingeniero Sandro',
            'name' : nombre,
            'correo' : correo,
            'telefono':telefono,
            'mensaje' :mensaje,
            'fecha' : fecha,
        })
        
        message = 'Solicitud de informacion'
        
        from_email = settings.EMAIL_HOST_USER 
        
        to_email = ['dilanfvalencia@gmail.com']
        subject = 'Solicitud de informacion '
        
        send_mail(subject,message ,  from_email, to_email, html_message=template)
        if send_mail:
        
            messages.success(request, 'Se envió tu correo. En breves nos pondremos en contacto contigo')
        
            return redirect('contacto')
                 

        template_name='registration/password_reset_done.html'
        
@login_required
def perfil(request):
    
        usuario_logeado = request.session.get('usuario_logeado') #Obtener el id del user logeado
    
        try:
                usuario = Usuario.objects.get(id = usuario_logeado)
                data = {'usuario': usuario}
                
                return render(request, 'paginas/perfil.html', data)
        except Usuario.DoesNotExist as e:
                messages.error(request, 'No se pudo encontrar el usuario')
                return redirect('/')

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
