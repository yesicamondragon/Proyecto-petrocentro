from django.urls import include, path
from . import views

urlpatterns = [
                 #Url de editar perfil
        path('perfil/', views.perfil, name="perfil"),
        path('editar_perfil/', views.editar_perfil, name="editar_perfil"),
        path('password_change/ <int:id>' , views.password_change, name="password_change"),
        path('delete-photo/', views.delete_photo, name='delete-photo'),
        #Url Configuración
        path('nosotros_conf/', views.configuracion_nosotros, name='nosotros_conf'),
        path('nosotros_foto/', views.agregar_fotos_nosotros, name="nosotros_foto"),
        path('eliminar-foto-nosotros/', views.eliminar_foto_nosotros, name="eliminar_foto_nosotros"),
        path('delete-photo-nosotros/', views.delete_photo_nosotros, name="delete-photo-nosotros"),
        path('editar-nosotros/<str:id>' , views.editar_nosotros, name="editar-nosotros"),
        
        #Url asignacionn de roles:
        path('asignar_roles/', views.roles, name="asignar_roles"),
        path('filtrar-permisos/', views.filtrar_permisos,name="filtrar-permisos"),
        path('aignar-permisos/<str:id>', views.agregar_permisos, name="asignar-permisos"),
        path('crear-rol/', views.crear_rol, name="crear-rol"),
        
        #url crear Post
        path('crear_post_view/', views.crear_post_view, name="crear_post_view"),
        
        path('crear_post/',views.crear_post, name="crear_post"),
        path('guardar_post/',views.guardar_post, name="guardar_post"),
        path('editar_post_view/<slug:slug>',views.editar_post_view, name="editar_post_view"),
        
        
]