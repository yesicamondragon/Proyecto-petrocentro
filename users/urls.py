from django.urls import include, path
from . import views

urlpatterns = [
        path('usuarios/', views.registrar_usuario, name='usuarios'),
        path('registro_usuarios/', views.registrar_usuario , name="registro_usuarios"),
        
        #Urls para los empleados,  registrar, editar y listar
        path('empleados/', views.listar_empleados, name='empleados'),
        path('editar_empleados/<str:id>/',views.editar_empleados,name="editar_empleados"),
        path('accounts/', include('django.contrib.auth.urls')),
        path('registrar_empleados/', views.registrar_empleados, name="registrar_empleados"),
        path('cambiar_estado/<int:id>', views.cambiar_estado, name="cambiar_estado"),

    
    ]