from django.db import models
from paginaPetrocentro.models import Usuario


class Categoria(models.Model):
        nombre = models.CharField('Nombre de la categoria',max_length=50, null=False, blank=False)
        estado = models.BooleanField('Categoria Activada/ Categoria no Activada', default=True)
        fecha_creacion = models.DateTimeField('Fecha de Creacion',auto_now=False,auto_now_add=True)
        
        class Meta:
                db_table="Categoria_blog"
                verbose_name = 'Categoría'
                verbose_name_plural = 'Categorías'
        def __str__(self):
                return self.nombre
        
class Post(models.Model):
        image = models.ImageField(upload_to="blog_images")
        titulo = models.CharField(max_length=90)
        categoria = models.ForeignKey(Categoria, blank=True, null=False, on_delete=models.CASCADE)
        descripcion = models.CharField(max_length=110)
        contenido = models.TextField()
        slug = models.CharField(max_length=100,)
        author = models.ForeignKey(Usuario, blank=True, null=True,on_delete=models.CASCADE)
        estado= models.BooleanField('Publicado/no Publicado', default=True)
        fecha_creacion = models.DateTimeField(auto_now_add=True)
        
        fecha_publicacion = models.DateTimeField(blank=True, null=True)
        fecha_fin = models.DateTimeField(blank=True, null=True)
        empleado = models.BooleanField('Empleados/ No Empleados', default=False)
        class Meta:
                db_table='Post'
                verbose_name = 'Post'
                verbose_name_plural = 'Posts'
        
        def __str__(self) :
                return self.titulo
        
class Suscriptores(models.Model):
        correo = models.CharField(max_length=50, null =True, blank=True )
        
        class Meta:
                db_table='Suscriptores'
                verbose_name = 'Suscriptor'
                verbose_name_plural = 'Suscriptores'
