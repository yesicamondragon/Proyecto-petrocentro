from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from blogs.models import *
from users.models import Empleado
from paginaPetrocentro.models import Usuario
from .forms import Form_post
import uuid
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from paginaPetrocentro.views import obtener_noticias_rss

# Create your views here.

def get_blog_context(request):
    """Helper para obtener el contexto común (usuario y empleado) de forma eficiente."""
    usuario_logeado_id = request.session.get('usuario_logeado')
    context = {}
    if usuario_logeado_id:
        try:
            usuario = Usuario.objects.get(id=usuario_logeado_id)
            context['usuario'] = usuario
            try:
                context['empleado'] = Empleado.objects.get(id=usuario.id)
            except Empleado.DoesNotExist:
                pass
        except Usuario.DoesNotExist:
            pass
    return context

def blog_view(request):
    """Muestra todas las noticias de todas las categorías (GENERAL)."""
    context = get_blog_context(request)
    busqueda = request.GET.get('busqueda')

    # --- CAMBIO CLAVE: Obtenemos todos los posts activos sin filtrar por categoría ---
    post = Post.objects.filter(estado=True)
    
    # Filtro de seguridad para contenido exclusivo de empleados
    if not context.get('empleado'):
        post = post.filter(empleado=False)
    
    if busqueda:
        post = post.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()
    
    # Solicitamos 12 posts (4 filas x 3 columnas) para la vista GENERAL
    posts_paginados = paginacion(request, post.order_by('-fecha_creacion'), 12)
    
    context['posts'] = posts_paginados
    context['busqueda'] = busqueda
    return render(request, 'blog/blog.html', context)
               
@login_required   
def crear_blog(request):
        context = get_blog_context(request)
        usuario = context.get('usuario')
        if request.method == 'POST':
                form = Form_post(request.POST, request.FILES)
                
                if form.is_valid():
                        cleaned_data = form.cleaned_data
                        slug = slugify(cleaned_data.get('titulo'))
                        original_slug = slug
                        queryset = Post.objects.filter(slug__startswith=slug)
                        if queryset.exists():
                                while queryset.exists():
                                        slug = f"{original_slug}-{uuid.uuid4().hex[:8]}"
                                        queryset = Post.objects.filter(slug__startswith=slug)
                                        
                        post = Post(
                                titulo=cleaned_data.get('titulo'), 
                                descripcion=cleaned_data.get('descripcion'), 
                                contenido=cleaned_data.get('contenido'), 
                                image=cleaned_data.get('image'), 
                                categoria= cleaned_data.get('categoria'),
                                author = usuario,
                                slug=slug,
                        )
                        post.save()
                        return redirect('blog')              

def post_detail_view(request, slug):
        context = get_blog_context(request)
        is_empleado = context.get('empleado') is not None

        if is_empleado:
                # Si es empleado, muestra todos los posts
                post = get_object_or_404(Post, slug=slug, estado=True)
                posts_relacionados = Post.objects.filter(estado=True).exclude(id=post.id).order_by('-fecha_creacion')[:2]
        else:
                # Si no es empleado, muestra solo los posts públicos
                post = get_object_or_404(Post, slug=slug, empleado=False)
                posts_relacionados = Post.objects.filter(empleado=False, estado=True).exclude(id=post.id).order_by('-fecha_creacion')[:2]

        context['post'] = post
        context['posts'] = posts_relacionados
        context['slug'] = post.slug
        return render(request, 'blog/detail_blog.html', context)

def paginacion( request, posts, num=6 ):
        paginator = Paginator(posts, num)
        page = request.GET.get('page')
        return paginator.get_page(page)

# Helper para obtener posts filtrados por categoría y visibilidad
def get_filtered_posts(request, category_name):
    busqueda = request.GET.get('busqueda')
    context = get_blog_context(request)
    is_empleado = context.get('empleado') is not None

    # Filtro base
    posts = Post.objects.filter(estado=True, categoria__nombre__iexact=category_name).order_by('-fecha_creacion')
    
    # Visibilidad
    if not is_empleado:
        posts = posts.filter(empleado=False)

    # Búsqueda
    if busqueda:
        posts = posts.filter(
            Q(titulo__icontains=busqueda) | Q(descripcion__icontains=busqueda) | Q(contenido__icontains=busqueda)
        ).distinct()

    context['posts'] = paginacion(request, posts)
    context['busqueda'] = busqueda
    return context

def tecnologia(request):
    context = get_filtered_posts(request, 'Tecnologia')
    return render(request, 'blog/tecnologia.html', context)
        
def medio_ambiente(request):
    context = get_filtered_posts(request, 'Medio_ambiente')
    return render(request, 'blog/medio_ambiente.html', context)

def economia(request):
    context = get_filtered_posts(request, 'economia')
    return render(request, 'blog/economia.html', context)

def politica(request):
    context = get_filtered_posts(request, 'politica')
    return render(request, 'blog/politica.html', context)

def hidrocarburos(request):
    context = get_filtered_posts(request, 'Hidrocarburos')
    return render(request, 'blog/hidrocarburos.html', context)

         
        