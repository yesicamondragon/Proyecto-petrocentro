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
from django.db.models import Q, Count
from django.core.paginator import Paginator
from paginaPetrocentro.views import obtener_noticias_rss

# Create your views here.

def get_blog_context(request):
    """Helper para obtener el contexto común (usuario, empleado y categorías) de forma eficiente."""
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
    # Agregamos las categorías globalmente para organizar la navegación del blog
    context['categorias_listado'] = Categoria.objects.annotate(
        total_posts=Count('post', filter=Q(post__estado=True))
    ).filter(total_posts__gt=0).order_by('nombre')
    
    # Habilitar visibilidad de inventario en el menú del Blog para administradores
    if request.user.is_superuser:
        context['inventario'] = 1

    return context

# Helper para obtener posts filtrados por nombre de categoría y visibilidad, y preparar el contexto
def get_blog_list_context(request, category_name=None):
    busqueda = request.GET.get('busqueda')
    context = get_blog_context(request) # Esto ya obtiene categorias_listado e info de usuario/empleado
    is_empleado = context.get('empleado') is not None

    posts_queryset = Post.objects.select_related('author', 'categoria').filter(estado=True).order_by('-fecha_creacion')
    current_category_obj = None

    if category_name and category_name.lower() != 'general':
        # Buscamos la categoría de forma segura. 
        # Intentamos primero coincidencia exacta de nombre.
        current_category_obj = Categoria.objects.filter(nombre__iexact=category_name).first()
        
        # Si no la encuentra, buscamos comparando la versión "slugificada" de los nombres
        # Esto permite que "/blog/medio-ambiente/" encuentre la categoría "Medio Ambiente"
        if not current_category_obj:
            for cat in Categoria.objects.all():
                if slugify(cat.nombre) == slugify(category_name):
                    current_category_obj = cat
                    break
        
        if current_category_obj:
            posts_queryset = posts_queryset.filter(categoria=current_category_obj)
    
    # Filtro de seguridad para contenido exclusivo de empleados
    if not context.get('empleado'):
        posts_queryset = posts_queryset.filter(empleado=False)

    if busqueda:
        posts_queryset = posts_queryset.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()

    context['posts'] = paginacion(request, posts_queryset, 12) # 12 posts por página

    # Cargar noticias externas solo si es la vista general (sin categoría específica)
    if not category_name or category_name.lower() == 'general':
        context['noticias_rss'] = obtener_noticias_rss()

    context['busqueda'] = busqueda
    context['current_category'] = current_category_obj # Pasar el objeto de categoría

    # Preparar información dinámica del encabezado para la plantilla
    if current_category_obj:
        context['titulo_pagina'] = f"Blog {current_category_obj.nombre}"
        # Mapear nombres de categoría a rutas de imagen estáticas. Usar nombre slugificado para consistencia.
        category_slug_for_image = slugify(current_category_obj.nombre).replace('-', '_')
        
        if category_slug_for_image == 'medio_ambiente':
            context['header_image'] = 'images/tierra.webp'
        elif category_slug_for_image == 'tecnologia':
            context['header_image'] = 'images/tecnologia.webp'
        elif category_slug_for_image == 'economia':
            context['header_image'] = 'images/economia.webp'
        elif category_slug_for_image == 'politica':
            context['header_image'] = 'images/politica.webp'
        elif category_slug_for_image == 'hidrocarburos':
            context['header_image'] = 'images/petroleo_blog.webp'
        else:
            context['header_image'] = 'images/INFORMACION.jpg' # Imagen por defecto para categorías desconocidas
        
        context['header_title_html'] = f"<h1>BLOG <br> {current_category_obj.nombre.upper()}</h1>"
        context['header_subtitle'] = "Blog Técnico de Petrocentro – Innovación y Servicios Oil & Gas en Colombia"
    else:
        context['titulo_pagina'] = "Noticias - Petrocentro S.A.S"
        context['header_image'] = 'images/INFORMACION.jpg'
        context['header_title_html'] = "<h1>Todas las Noticias</h1>"
        context['header_subtitle'] = "Actualidad Técnica de Petrocentro – Innovación y Servicios Oil & Gas en Colombia"

    return context

def blog_view(request, category_name=None): # Modificar la vista existente para aceptar category_name
    """Muestra todas las noticias o noticias de una categoría específica."""
    context = get_blog_list_context(request, category_name)
    return render(request, 'blog/blog.html', context)
               
def post_detail_view(request, slug):
        context = get_blog_context(request)
        is_empleado = context.get('empleado') is not None

        # Base del queryset para evitar redundancia
        base_queryset = Post.objects.select_related('author', 'categoria').filter(estado=True)

        if is_empleado:
                post = get_object_or_404(base_queryset, slug=slug)
                posts_relacionados = base_queryset.exclude(id=post.id).order_by('-fecha_creacion')[:2]
        else:
                post = get_object_or_404(base_queryset.filter(empleado=False), slug=slug)
                posts_relacionados = base_queryset.filter(empleado=False).exclude(id=post.id).order_by('-fecha_creacion')[:2]

        context['post'] = post
        context['posts'] = posts_relacionados
        context['slug'] = post.slug
        return render(request, 'blog/detail_blog.html', context)

def paginacion( request, posts, num=6 ):
        paginator = Paginator(posts, num)
        page = request.GET.get('page')
        return paginator.get_page(page)

# Helper para obtener posts filtrados por categoría y visibilidad