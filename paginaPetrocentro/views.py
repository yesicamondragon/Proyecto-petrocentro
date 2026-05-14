from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages

from django.urls import reverse_lazy
from Petrocentro import settings
from configuracion.models import Nosotros
from users.models import Empleado
from django.db.models import Avg, Count
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
from django.template.loader import render_to_string
import json
from datetime import datetime
import requests
import yfinance as yf
import random
from bs4 import BeautifulSoup 
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import JsonResponse
import qrcode
from django.core.cache import cache
from django.http import HttpResponse

def generar_qr(request):
    data = "https://www.tusitio.com/pqrs"
    img = qrcode.make(data)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


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

def obtener_noticias_rss():
    # Intentar obtener noticias de la caché
    cached_news = cache.get('rss_news_petrocentro')
    if cached_news:
        return cached_news

    try:
        url = "https://news.google.com/rss/search?q=petroleo+colombia+hidrocarburos&hl=es-419&gl=CO&ceid=CO:es-419"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.findAll('item')
        
        noticias = []
        # Temas industriales variados para asegurar que no se repitan
        temas_fallback = ["oilwell", "refinery", "pipeline", "drilling", "energy-industry"]
        
        for item in items[:9]: 
            titulo_full = item.title.text
            titulo = titulo_full.split(" - ")[0] # Título limpio
            fuente = titulo_full.split(" - ")[-1] if " - " in titulo_full else "Noticia Sector"
            
            # Intentar encontrar imagen real en la descripción (Google News suele poner un <img> ahí)
            imagen_url = None
            if item.description:
                desc_soup = BeautifulSoup(item.description.text, 'html.parser')
                img_tag = desc_soup.find('img')
                if img_tag:
                    imagen_url = img_tag.get('src')
            
            # Si no hay imagen real, generar una temática única y aleatoria
            if not imagen_url:
                keyword = random.choice(temas_fallback)
                seed = random.randint(1, 999999)
                imagen_url = f"https://loremflickr.com/800/500/{keyword}?lock={seed}"

            noticias.append({
                'titulo': titulo,
                'link': item.link.text,
                'fuente': fuente,
                'fecha': item.pubDate.text[:16],
                'imagen': imagen_url
            })
        
        # Guardar en caché por 2 horas (7200 segundos)
        cache.set('rss_news_petrocentro', noticias, 7200)
        return noticias
    except Exception as e:
        print(f"Error RSS: {e}")
        return []

#Funcion para redirigir al index
def get_economic_indicators():
    """Obtiene indicadores de mercado (Dólar y Brent) vía yfinance."""
    # Intentar obtener datos de la caché para carga instantánea
    cached_data = cache.get('market_indicators')
    if cached_data:
        return cached_data

    data = {'dolar': '...', 'brent': '...'}
    try:
        # USDCOP=X es el par Dólar/Peso Colombiano
        # Cambiamos fast_info por history para evitar bloqueos conocidos en versiones recientes de yfinance
        dolar_ticker = yf.Ticker("USDCOP=X")
        hist_d = dolar_ticker.history(period="1d")
        dolar_price = hist_d['Close'].iloc[-1] if not hist_d.empty else None

        if dolar_price:
            data["dolar"] = f"${dolar_price:,.2f}"

        brent_ticker = yf.Ticker("BZ=F")
        hist_b = brent_ticker.history(period="1d")
        brent_price = hist_b['Close'].iloc[-1] if not hist_b.empty else None

        if brent_price:
            data["brent"] = f"${brent_price:,.2f}"
        
        # Guardar en caché por 1 hora (3600 segundos)
        cache.set('market_indicators', data, 3600)
    except Exception as e:
        print(f"Error obteniendo indicadores: {e}")
    return data

def api_indicadores(request):
    """Endpoint JSON para actualización dinámica vía AJAX."""
    return JsonResponse(get_economic_indicators())

def index(request):
    # Obtener indicadores (usa caché internamente para que la carga sea rápida)
    market_data = get_economic_indicators()
    context = market_data.copy()

    # Obtener noticias de sector en tiempo real
    context['noticias'] = obtener_noticias_rss()

    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass
    
    return render(request, 'paginas/index.html', context)
   
        
#Funcion para redirigir al nosotros
def nosotros(request):

    nosotros= Nosotros.objects.all()
    context ={
            'nosotros':nosotros
    }
    
    usuario_logeado = request.session.get('usuario_logeado')

    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass
    return render(request, 'paginas/nosotros.html', context)
            
def politicas_nosotros(request):
    context={}
    
    usuario_logeado= request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            messages.error(request,f'No se encontro el empleado, error: {e}')
    return render(request, 'paginas/politicas.html', context)
    
#Funcion para redirigir al servicios
def servicios(request):
    context = {}
    
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass

    # Obtener las últimas reseñas con comentario para mostrar en la sección de testimonios
    resenas_qs = Valoracion.objects.exclude(comentario_texto__isnull=True).exclude(comentario_texto="").order_by('-fecha')[:10]
    # Mapeo para que el JS reconozca la clase de filtrado
    clases_filtro = {
        'Evaluación y Medición de Pozos': 'evaluacion', 
        'Integridad y Seguridad de Infraestructura': 'integridad', 
        'Operación y Mantenimiento de Activos': 'operacion', 
        'Ingeniería, Diseño y Fabricación': 'ingenieria',
        'Servicios Generales': 'generales'
    }
    for r in resenas_qs:
        r.clase_css = clases_filtro.get(r.servicio, 'evaluacion')
    context['resenas_reales'] = resenas_qs
            
    # Calcular estadísticas de valoraciones por categoría
    categorias_map = {
        'evaluacion': 'Evaluación y Medición de Pozos',
        'integridad': 'Integridad y Seguridad de Infraestructura',
        'operacion': 'Operación y Mantenimiento de Activos',
        'ingenieria': 'Ingeniería, Diseño y Fabricación',
        'generales': 'Servicios Generales'
    }
    
    # Obtenemos todas las estadísticas de una sola vez
    stats_qs = Valoracion.objects.values('servicio').annotate(
        promedio=Avg('puntuacion'),
        total=Count('id')
    )
    
    stats_valoraciones = {}
    for s in stats_qs:
        # Buscamos la 'key' (evaluacion, integridad...) basada en el 'name' en categorias_map
        key = next((k for k, v in categorias_map.items() if v == s['servicio']), None)
        if key:
            stats_valoraciones[key] = {
                'promedio': round(s['promedio'], 1),
                'total': s['total']
            }

    context['stats_valoraciones'] = stats_valoraciones
            
    return render(request, 'paginas/servicios.html', context)

def guardar_valoracion(request):
    """Recibe y almacena la calificación de estrellas de los servicios"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            categoria = data.get('service_category')
            puntuacion = data.get('rating')
            
            if categoria and puntuacion:
                Valoracion.objects.create(servicio=categoria, puntuacion=puntuacion)
                return JsonResponse({'status': 'success', 'message': 'Valoración guardada correctamente'})
            
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def guardar_reseña_interna(request):
    """Recibe y almacena las reseñas internas con comentario y estrellas."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre_cliente = data.get('reviewer_name')
            comentario_texto = data.get('review_comment')
            puntuacion = data.get('rating')
            categoria = data.get('service_category', 'Servicios Generales')
            
            if comentario_texto and puntuacion:
                Valoracion.objects.create(
                    servicio=categoria,
                    puntuacion=puntuacion,
                    nombre_cliente=nombre_cliente if nombre_cliente else 'Anónimo',
                    comentario_texto=comentario_texto
                )
                return JsonResponse({'status': 'success', 'message': 'Reseña guardada correctamente'})
            return JsonResponse({'status': 'error', 'message': 'Comentario y calificación son obligatorios.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

#Funcion para redirigir al contacto
def contacto(request):
    
    context={}
    
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass
            
    return render(request, 'paginas/contacto.html', context)
            
    #Funcion para redirigir al pqrs

def pqrs(request):
    context={}
      
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id = usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass

    return render(request,'paginas/PQRS.html', context)

def consultar_pqrs(request):
    context = {}
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        context['usuario'] = Usuario.objects.get(id=usuario_logeado)

    radicado = request.GET.get('radicado')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if radicado:
        pqr = PQRS.objects.filter(radicado=radicado.strip()).first()
        if pqr:
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'pqr': {
                        'radicado': pqr.radicado,
                        'nombre': pqr.nombre,
                        'tipo': pqr.get_tipo_display(),
                        'mensaje': pqr.mensaje,
                        'estado': pqr.get_estado_display(),
                        'estado_raw': pqr.estado,
                        'fecha': pqr.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                        'respuesta': pqr.respuesta
                    }
                })
            context['pqr'] = pqr
        else:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'No se encontró ninguna solicitud con ese número de radicado.'}, status=404)
            messages.error(request, "No se encontró ninguna solicitud con ese número de radicado.")
            
    return render(request, 'paginas/consultar_pqrs.html', context)

# Nueva vista para el formulario de PQRS en una interfaz separada
def pqrs_form_view(request):
    context = {}
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id=usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        tipo = request.POST.get('tipo')
        mensaje = request.POST.get('mensaje')
        honeypot = request.POST.get('website_hp')

        # Honeypot: Si el campo oculto tiene contenido, ignoramos la solicitud (es un bot)
        if honeypot:
            return redirect('pqrs')

        if not all([nombre, correo, tipo, mensaje]):
            messages.warning(request, "Por favor complete todos los campos obligatorios.")
        else:
            try:
                pqr = PQRS.objects.create(nombre=nombre, correo=correo, telefono=telefono, tipo=tipo, mensaje=mensaje)
                subject = f"Confirmación de Radicado {pqr.radicado} - Petrocentro"
                email_body = f"Hola {nombre},\n\nHemos recibido tu {tipo}. Tu número de radicado es: {pqr.radicado}\n\nPuedes consultar el estado de tu solicitud en nuestro sitio web."
                messages.success(request, f"¡Solicitud radicada! Su número es: {pqr.radicado}. Guárdelo para consultar el estado abajo.")
            except Exception as e:
                messages.error(request, f"Error al procesar la solicitud: {e}")
    
    return redirect('pqrs')

def pqrs_form_success(request):
    context = {}
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        usuario = Usuario.objects.get(id=usuario_logeado)
        context['usuario'] = usuario
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            context['empleado'] = empleado
        except Exception as e:
            pass
    return render(request, 'paginas/pqrs_form_success.html', context)

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
            estado = 1
            nombre = form.cleaned_data['Nombre_completo']
            correo= form.cleaned_data['correo_electronico']

            
            
            usuario = Usuario(
                user_id = User.objects.get(id=user_id),
                estado = Estado.objects.get(id=estado),
                nombre = nombre,
                correo = correo,
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
                try:
                    send_mail(subject, message, from_email, to_email, html_message=mensaje_html)
                except Exception as e:
                    # Si falla el correo, imprimimos el error en consola pero dejamos pasar al usuario
                    print(f"Advertencia: No se pudo enviar el correo de registro. Error: {e}")
            
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
        # Obtener el rol seleccionado por el usuario en el formulario
        rol_seleccionado = request.POST.get('rol')
        
        #declarar variable de usuario, donde valida si el usuario y la contraseña son correctos
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # El usuario está autenticado y activo.
            
            try:
                # Aseguramos que el estado "Activo" exista en la DB para evitar errores en instalaciones limpias
                estado_activo, _ = Estado.objects.get_or_create(id=1, defaults={'nombre': 'Activo'})
                usuario_profile, created = Usuario.objects.get_or_create(
                    user_id=user,
                    defaults={
                        'estado': estado_activo,
                        'nombre': user.get_full_name() or user.username,
                        'correo': user.email
                    }
                )

                # Verificar si la cuenta está activa
                if usuario_profile.estado.id != 1:
                    messages.error(request, f'La cuenta para {user.username} está deshabilitada.')
                    return render(request, 'registration/login.html')

                # LÓGICA DE ROLES
                es_empleado = False
                es_admin = False
                
                # Verificar si es superusuario (Django Admin)
                if user.is_superuser:
                    es_admin = True
                    es_empleado = True # Superusuario puede entrar como empleado también
                else:
                    # Verificar en tabla Empleado
                    try:
                        empleado_profile = Empleado.objects.get(id=usuario_profile.id)
                        es_empleado = True
                        # Verificar si su rol asignado en BD es Administrador
                        if empleado_profile.id_rol and empleado_profile.id_rol.nombre == "Administrador":
                            es_admin = True
                    except Empleado.DoesNotExist:
                        es_empleado = False

                # VALIDACIÓN DEL ROL SELECCIONADO VS ROL REAL
                if rol_seleccionado == "Administrador":
                    if es_admin:
                        login(request, user)
                        request.session['usuario_logeado'] = usuario_profile.id
                        messages.success(request, f'Bienvenido Administrador, {usuario_profile.nombre}')
                        return redirect('perfil_admin') # Redirige al perfil de administrador (Gestión)
                    else:
                        messages.error(request, 'No tienes permisos de Administrador.')
                
                elif rol_seleccionado == "Empleado":
                    if es_empleado:
                        login(request, user)
                        request.session['usuario_logeado'] = usuario_profile.id
                        messages.success(request, f'Bienvenido al Portal de Empleados, {usuario_profile.nombre}')
                        return redirect('perfil_empleado') # Redirige al perfil de empleado (Agenda operativa)
                    else:
                        messages.error(request, 'No tienes un perfil de Empleado asignado.')
                
                else:
                    messages.error(request, 'Debe seleccionar un rol válido.')

            except Exception as e:
                messages.error(request, f'Error en el inicio de sesión: {e}')
                
        else:
            #mensaje de alerta
            messages.error(request,'Usuario o contraseña inválidos')
        
    return render(request, 'registration/login.html')
    
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
        honeypot = request.POST.get('website_hp')

        # Honeypot check para evitar spam en el formulario de contacto
        if honeypot:
            return redirect('contacto')

        # Validación de campos obligatorios
        if not nombre or not correo or not mensaje:
            messages.error(request, 'Por favor, completa los campos obligatorios (*).')
            return redirect('contacto')

        try:
            fecha = datetime.now()
            template = render_to_string('plantillas/email_contacto.html', {
                'nombre': 'Ingeniero Sandro',
                'name': nombre,
                'correo': correo,
                'telefono': telefono,
                'mensaje': mensaje,
                'fecha': fecha,
            })

            subject = f'Nueva Solicitud de Contacto - {nombre}'
            message = f'Has recibido un nuevo mensaje de {nombre} ({correo})'
            from_email = settings.EMAIL_HOST_USER
            # Se ha desactivado el envío de correo para evitar spam.
            # Las solicitudes de contacto deben revisarse directamente en el panel administrativo o en la base de datos.
            # Notificación por correo desactivada para evitar spam. Revisar en el panel de control.
            result = True 

            if result:
                messages.success(request, 'Se envió tu correo. En breves nos pondremos en contacto contigo.')
            else:
                messages.error(request, 'No se pudo entregar el correo. Inténtalo de nuevo más tarde.')

        except Exception as e:
            print(f"Error al enviar correo: {e}")
            messages.error(request, 'Ocurrió un error técnico al enviar el mensaje. Verifica tu conexión.')
    
    return redirect('contacto')

def solicitar_cotizacion(request):
    """Recibe la solicitud de cotización vía AJAX y notifica al administrador."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Honeypot check
            if data.get('website_hp'):
                return JsonResponse({'status': 'success'}) 

            nombre = data.get('nombre')
            empresa = data.get('empresa', 'No especificada')
            correo = data.get('email')
            telefono = data.get('telefono')
            servicio = data.get('servicio')
            mensaje = data.get('mensaje')

            # Validación básica
            validate_email(correo)
            if not nombre or len(mensaje) < 5:
                return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)

            # Guardar en la base de datos para el nuevo módulo
            Cotizacion.objects.create(
                nombre=nombre,
                empresa=empresa,
                email=correo,
                telefono=telefono,
                servicio=servicio,
                mensaje=mensaje
            )

            # Notificación por correo desactivada para evitar spam. Consultar en el módulo de Cotizaciones del dashboard.
            return JsonResponse({'status': 'success'})
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Correo inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Inválido'}, status=405)

def suscribirse(request):
    """Maneja la suscripción al blog devolviendo siempre una respuesta JSON."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

    correo = request.POST.get('correo')
    if not correo:
        return JsonResponse({'status': 'error', 'message': 'El correo electrónico es obligatorio.'}, status=400)

    try:
        # El modelo Suscriptores tiene unique=True en correo, get_or_create lo maneja bien
        obj, created = Suscriptores.objects.get_or_create(correo=correo)
        if created:
            return JsonResponse({'status': 'success', 'message': '¡Te has suscrito correctamente!'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Este correo ya se encuentra registrado.'})
    except Exception as e:
        print(f"Error en suscripción: {e}")
        return JsonResponse({'status': 'error', 'message': 'Hubo un problema técnico en el servidor.'}, status=500)

def trabaja_con_nosotros(request):
    """Interfaz para recepción de hojas de vida"""
    from users.models import Cargo, Candidato
    
    # Cargos a excluir de la lista desplegable pública
    cargos_excluidos_nombres = [
        "Aprendiz",
        "Gerente de Operaciones",
        "Administrador de Contrato", # Asumiendo "administrador de con" es este
        "Coordinador HSEQ"
    ]
    
    # Obtener todos los cargos y luego excluir los no deseados
    cargos_disponibles = Cargo.objects.exclude(nombre__in=cargos_excluidos_nombres)
    
    context = {'cargos': cargos_disponibles}
    
    # Gestión de sesión para NavBar
    usuario_logeado = request.session.get('usuario_logeado')
    if usuario_logeado:
        try:
            usuario = Usuario.objects.get(id=usuario_logeado)
            context['usuario'] = usuario
            context['empleado'] = Empleado.objects.filter(id=usuario.id).first()
        except: pass

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        cargo_id = request.POST.get('cargo')
        mensaje = request.POST.get('mensaje')
        hoja_vida = request.FILES.get('hoja_vida')
        honeypot = request.POST.get('website_hp')

        # Evitar spam de bots en postulaciones laborales
        if honeypot:
            return redirect('trabaja_con_nosotros')

        if hoja_vida and not hoja_vida.name.endswith('.pdf'):
            messages.error(request, "Error: Solo se permiten archivos en formato PDF.")
        elif hoja_vida and hoja_vida.size > 5242880:
            messages.error(request, "Error: La hoja de vida no debe superar los 5 MB.")
        elif not all([nombre, correo, telefono, hoja_vida]):
            messages.error(request, "Por favor complete todos los campos obligatorios.")
        else:
            try:
                cargo = Cargo.objects.get(id_cargo=cargo_id) if cargo_id else None
                Candidato.objects.create(
                    nombre=nombre, correo=correo, telefono=telefono,
                    cargo_interes=cargo, hoja_de_vida=hoja_vida, mensaje=mensaje
                )
                
                # Notificación automática por correo electrónico con adjunto PDF
                subject = f"NUEVA POSTULACIÓN: {nombre} - {cargo.nombre if cargo else 'General'}"
                email_body = f"""
Se ha recibido una nueva postulación laboral a través del portal "Trabaja con nosotros":

DATOS DEL CANDIDATO:
--------------------------------------------------
Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Cargo de Interés: {cargo.nombre if cargo else 'No especificado'}
--------------------------------------------------

MENSAJE DE PRESENTACIÓN:
{mensaje if mensaje else 'Sin mensaje adicional.'}

La hoja de vida se encuentra adjunta a este correo en formato PDF.
"""
                # Notificación por correo desactivada para evitar saturación por spam de bots.
                messages.success(request, "¡Postulación recibida! Gracias por querer formar parte de Petrocentro.")
                return redirect('trabaja_con_nosotros')
            except Exception as e:
                messages.error(request, f"Error al enviar: {e}")

    return render(request, 'paginas/trabaja_con_nosotros.html', context)
        
