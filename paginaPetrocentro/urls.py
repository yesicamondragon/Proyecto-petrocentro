from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView

sitemaps = {
    'sitemap': StaticViewSitemap,  # Incluimos el sitemap de las vistas estáticas
}
urlpatterns = [
    
    path ('', views.index , name='index'),
    
    path('registro/', views.registro, name="registro"),
    path('nosotros/', views.nosotros, name="nosotros"),
    path('contacto/', views.contacto, name="contacto"),
    path('pqrs/', views.pqrs, name="pqrs"),
    path('servicios/', views.servicios, name="servicios"),
    
    path('login_view/', views.login_view, name="login_view"),
    path('logout_view/', views.logout_view, name="logout_view"),
    
    #Restablecer contraseña personalizado. 
    path('password_reset/', CustomPasswordResetView.as_view(
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    
    path('contacto_correo/', views.contacto_mensaje, name="contacto_correo"),
    

    
    path("politicas_nosotros/", views.politicas_nosotros , name="politicas_nosotros"),
    #Url reset password
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
