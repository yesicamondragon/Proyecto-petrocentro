
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Estado(models.Model):
    
    nombre = models.CharField(max_length=15)
    id = models.AutoField(primary_key=True)
    
    class Meta:
        db_table="usuario_estado"
        ordering = ["nombre"]
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
    

class Usuario(models.Model):
    id=models.AutoField(primary_key=True, null=False)   
    foto_perfil = models.ImageField(null=True, blank=True, upload_to="Fotos_perfil")
    user_id =models.ForeignKey(User, on_delete=models.CASCADE)
    estado=models.ForeignKey(Estado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=60,null=False)
    correo = models.EmailField(max_length=50, null=False)


    class Meta:
            db_table="usuario"
            ordering = ["nombre"]
            verbose_name = "Usuario"
            verbose_name_plural = "Usuarios"