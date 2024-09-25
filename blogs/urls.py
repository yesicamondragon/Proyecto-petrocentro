from django.urls import path

from blogs import views

urlpatterns = [
        path('blog', views.blog_view, name="blog"),

        path('blog/tecnologia/', views.tecnologia,name="tecnologia"),
        path('blog/medio_ambiente', views.medio_ambiente,name="medio_ambiente"),
        path('blog/politica', views.politica,name="politica"),
        path('blog/economia', views.economia,name="economia"),
        path('blog/hidrocarburos', views.hidrocarburos,name="hidrocarburos"),
        
        path('suscribirse/', views.suscribir, name="suscribirse"),
        path('blog/<slug:slug>', views.post_detail_view,name="detail-post"),
        

]