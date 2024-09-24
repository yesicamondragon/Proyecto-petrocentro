from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from blogs.models import *
from users.models import Empleado
from django.contrib.auth.models import User as Usuario
from paginaPetrocentro.models import Usuario
from .forms import Form_post
import uuid
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.


def blog_view(request):
    usuario_logeado = request.session.get('usuario_logeado')
    busqueda = request.GET.get('busqueda')
    
    # Inicializar queryset base
    post = Post.objects.filter(estado=True)
    
    if usuario_logeado:
        usuario = Usuario.objects.get(id=usuario_logeado)
        try:
            empleado = Empleado.objects.get(id=usuario.id)
            # Si es empleado, mostrar todos los posts
        except Empleado.DoesNotExist:
            # Si no es empleado, filtrar los posts
            post = post.filter(empleado=False)
    else:
        # Si no está logueado, filtrar los posts
        post = post.filter(empleado=False)
    
    # Aplicar búsqueda si existe
    if busqueda:
        post = post.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()
    
    # Ordenar y paginar
    post = post.order_by('-fecha_creacion')
    paginator = Paginator(post, 6)
    page = request.GET.get('page')
    post = paginator.get_page(page)
    
    # Preparar contexto
    context = {
        'posts': post,
    }
    
    if usuario_logeado:
        context['usuario'] = usuario
        if 'empleado' in locals():
            context['empleado'] = empleado
    
    return render(request, 'blog/blog.html', context)
    
               
@login_required   
def crear_blog(request):
        usuario_logeado = request.session.get('usuario_logeado')
        usuario_logeado = Usuario.objects.get(id = usuario_logeado)
        if request.method == 'POST':
                form = Form_post(request.POST, request.FILES)
                
                if form.is_valid():
                        cleaned_data = form.cleaned_data
                        titulo = cleaned_data.get('titulo')
                        descripcion = cleaned_data.get('descripcion')
                        contenido = cleaned_data.get('contenido')
                        image = cleaned_data.get('image')
                        categoria = cleaned_data.get('categoria')
                        
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
                                image=image, 
                                categoria= categoria,
                                author = Usuario.objects.get(id =usuario_logeado.id ),
                                slug=slug,
                                
                        )
                        post.save()
                        return redirect('blog')              

def post_detail_view(request, slug):
        context = {}
        usuario_logeado = request.session.get('usuario_logeado')

        if usuario_logeado:
                try:
                        usuario = Usuario.objects.get(id=usuario_logeado)
                        context['usuario'] = usuario

                        try:
                                emp = Empleado.objects.get(id=usuario.id)
                                context['empleado'] = emp
                                # Si es empleado, muestra todos los posts
                                post = get_object_or_404(Post, slug=slug)
                                posts = Post.objects.exclude(id=post.id).order_by('-fecha_creacion')[:2]
                        except Empleado.DoesNotExist:
                                # Si no es empleado, muestra solo los posts que no son para empleados
                                post = get_object_or_404(Post, slug=slug, empleado=False)
                                posts = Post.objects.filter(empleado=False).exclude(id=post.id).order_by('-fecha_creacion')[:2]
                except Usuario.DoesNotExist:
                # Manejar el caso en que el usuario no existe
                        post = get_object_or_404(Post, slug=slug, empleado=False)
                        posts = Post.objects.filter(empleado=False).exclude(id=post.id).order_by('-fecha_creacion')[:2]
        else:
                # Si no está logueado, muestra solo los posts que no son exclusivos para empleados
                post = get_object_or_404(Post, slug=slug, empleado=False)
                posts = Post.objects.filter(empleado=False).exclude(id=post.id).order_by('-fecha_creacion')[:2]

        context['post'] = post
        context['posts'] = posts
        context['slug'] = post.slug

        return render(request, 'blog/detail_blog.html', context)

#Busqueda funcion
def obtener_post(busqueda=None, categoria=None,empleado = None):
        categoria = Categoria.objects.get(nombre__iexact = categoria)
        if empleado == None:
                post = Post.objects.filter(estado=True, categoria = categoria).order_by('-fecha_creacion')
        else:
                post = Post.objects.filter(estado=True, categoria = categoria, empleado = empleado).order_by('-fecha_creacion')
       
                   
        if busqueda:
                post = post.filter(
                        Q(titulo__icontains=busqueda) |
                        Q(descripcion__icontains=busqueda)|
                        Q(contenido__icontains=busqueda) ,
                        estado = True,
                        categoria = categoria
                        
                ).distinct().order_by('-fecha_creacion')
        return post

def paginacion( request, posts ):
        paginator = Paginator(posts, 6)
        page = request.GET.get('page')
        return paginator.get_page(page)

def tecnologia(request):
        usuario_logeado = request.session.get('usuario_logeado')
        busqueda = request.GET.get('busqueda')
        post = obtener_post(busqueda,'Tecnologia', False)            
        post = paginacion(request,post)
        
        context= {
                'posts': post,
        }
        usuario_logeado = request.session.get('usuario_logeado')
        if usuario_logeado:
                usuario = Usuario.objects.get(id=usuario_logeado)
                context['usuario'] = usuario
                try:
                        empleado = Empleado.objects.get(id=usuario.id)
                        post = obtener_post(busqueda,'Tecnologia')                        
                        post = paginacion(request,post)
                        context['empleado'] = empleado
                        context['posts'] = post  
                        
                # Si es empleado, mostrar todos los posts
                except Empleado.DoesNotExist:
                # Si no es empleado, filtrar los posts
                     pass
                
        return render(request, 'blog/tecnologia.html', context)
        
def medio_ambiente(request):
        busqueda = request.GET.get('busqueda')
        
        post = obtener_post(busqueda,'Medio_ambiente',False)
        post = paginacion(request, post)
        
        context={
                'posts': post,
        }
        usuario_logeado = request.session.get('usuario_logeado')
        if usuario_logeado:
                usuario = Usuario.objects.get(id = usuario_logeado)
                context['usuario'] = usuario
                try:
                        empleado = Empleado.objects.get(id = usuario.id)
                        post = obtener_post(busqueda,'Medio_ambiente')
                        post = paginacion(request,post)
                        context['posts'] = post  
                        context['empleado'] = empleado
                        
                except:
                        pass
     
        return render(request,'blog/medio_ambiente.html',context)

def economia(request):
        busqueda = request.GET.get('busqueda')
        
        post = obtener_post(busqueda,'economia',False)
        post = paginacion(request, post)
        
        context={
                'posts': post,
        }
        
        usuario_logeado = request.session.get('usuario_logeado')
        
        if usuario_logeado:
                usuario = Usuario.objects.get(id = usuario_logeado)
                context['usuario'] = usuario
                try:
                        empleado = Empleado.objects.get(id = usuario.id)
                        post = obtener_post(busqueda,'economia')
                        post = paginacion(request, post)
                        context['posts'] = post                        
                        context['empleado'] = empleado
                except:
                        pass
        
        return render(request,'blog/economia.html',context)

def politica(request):
        busqueda = request.GET.get('busqueda')
        
        post = obtener_post(busqueda,'politica',False)
        post = paginacion(request, post)
        
        context= {
                'posts': post,
        }
        
        usuario_logeado = request.session.get('usuario_logeado')
        
        if usuario_logeado:
                usuario = Usuario.objects.get(id = usuario_logeado)
                context['usuario'] = usuario
                try:
                        empleado = Empleado.objects.get(id = usuario.id)
                        post = obtener_post(busqueda,'politica')
                        post = paginacion(request, post)
                        context['posts'] = post 
                        context['empleado'] = empleado
                except:
                        pass
        return render(request,'blog/politica.html',context)

def hidrocarburos(request):
        busqueda = request.GET.get('busqueda')        
       
        post = obtener_post(busqueda,'hidrocarburos')
        post = paginacion(request, post)
        
        context= {
                'posts': post,
        }
        
        usuario_logeado = request.session.get('usuario_logeado')
        
        if usuario_logeado:
                usuario = Usuario.objects.get(id = usuario_logeado)
                context['usuario'] = usuario
                try:
                        empleado = Empleado.objects.get(id = usuario.id)
                        post = obtener_post(busqueda,'hidrocarburos')
                        post = paginacion(request, post)
                        context['posts'] = post 
                        context['empleado'] = empleado
                except:
                        pass
        
        return render(request,'blog/hidrocarburos.html',context)

def suscribir(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            if Suscriptores.objects.filter(correo=email).exists():
                return JsonResponse({'success': False, 'error': 'Este email ya está suscrito.'})
            else:
                suscripcion = Suscriptores(correo=email)
                suscripcion.save()
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
                
        

         
        