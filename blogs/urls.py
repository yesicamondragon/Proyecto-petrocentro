from django.urls import path

from blogs import views

urlpatterns = [
        path('blog', views.blog_view, name="blog"),

        path('blog/<str:category_name>/', views.blog_view, name='blog_category'), # Ruta genérica para categorías

        path('blog/<slug:slug>', views.post_detail_view,name="detail-post"),
        

]