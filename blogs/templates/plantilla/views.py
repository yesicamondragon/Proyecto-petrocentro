from django.shortcuts import render, get_object_or_404
from blogs.models import Post, Categoria # Asumiendo que estos modelos están definidos en blogs/models.py
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import Usuario, Empleado, Rol_permiso # Asumiendo que estos son accesibles
from configuracion.views import obtener_permisos # Asumiendo que este helper es accesible

def get_common_blog_context(request):
    """Helper para obtener el contexto común para las vistas del blog."""
    context = {
        'usuario': None,
        'empleado': None,
        'nombre_rol': 'Visitante',
        'crear': 0, 'consultar': 0, 'editar': 0, 'eliminar': 0, 'usuarios': 0,
    }
    usuario_logeado_id = request.session.get('usuario_logeado')
    if usuario_logeado_id:
        usuario_profile = get_object_or_404(Usuario, id=usuario_logeado_id)
        context['usuario'] = usuario_profile
        try:
            empleado_profile = Empleado.objects.get(id=usuario_profile.id)
            context['empleado'] = empleado_profile
            if empleado_profile.id_rol:
                context['nombre_rol'] = empleado_profile.id_rol.nombre
                permisos_qs = Rol_permiso.objects.filter(rol=empleado_profile.id_rol)
                context.update(obtener_permisos(permisos_qs))
            else:
                context['nombre_rol'] = "Empleado (Sin Rol)"
        except Empleado.DoesNotExist:
            pass # El usuario está logeado pero no es un empleado
    return context

def blog(request):
    """
    Vista para la página principal del blog (categoría 'GENERAL').
    Muestra todas las publicaciones de todas las categorías.
    """
    common_context = get_common_blog_context(request)
    busqueda = request.GET.get('busqueda')
    
    # --- MODIFICACIÓN CLAVE: Obtener TODAS las publicaciones ---
    posts_list = Post.objects.all().order_by('-fecha_creacion')
    # --- FIN MODIFICACIÓN ---

    if busqueda:
        posts_list = posts_list.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()

    paginator = Paginator(posts_list, 6) # Asumiendo 6 posts por página
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'busqueda': busqueda,
    }
    context.update(common_context) # Fusionar el contexto común
    return render(request, 'blogs/blog/blog.html', context)

def tecnologia(request):
    """
    Vista para la categoría 'TECNOLOGIA'.
    Muestra solo las publicaciones de esta categoría.
    """
    common_context = get_common_blog_context(request)
    busqueda = request.GET.get('busqueda')
    posts_list = Post.objects.filter(categoria__nombre='TECNOLOGIA').order_by('-fecha_creacion')

    if busqueda:
        posts_list = posts_list.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()

    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'busqueda': busqueda,
    }
    context.update(common_context)
    return render(request, 'blogs/blog/blog.html', context)

def medio_ambiente(request):
    """
    Vista para la categoría 'M/AMBIENTE'.
    Muestra solo las publicaciones de esta categoría.
    """
    common_context = get_common_blog_context(request)
    busqueda = request.GET.get('busqueda')
    posts_list = Post.objects.filter(categoria__nombre='M/AMBIENTE').order_by('-fecha_creacion')

    if busqueda:
        posts_list = posts_list.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()

    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'busqueda': busqueda,
    }
    context.update(common_context)
    return render(request, 'blogs/blog/blog.html', context)

def hidrocarburos(request):
    """
    Vista para la categoría 'HIDROCARBUROS'.
    Muestra solo las publicaciones de esta categoría.
    """
    common_context = get_common_blog_context(request)
    busqueda = request.GET.get('busqueda')
    posts_list = Post.objects.filter(categoria__nombre='HIDROCARBUROS').order_by('-fecha_creacion')

    if busqueda:
        posts_list = posts_list.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        ).distinct()

    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'busqueda': busqueda,
    }
    context.update(common_context)
    return render(request, 'blogs/blog/blog.html', context)