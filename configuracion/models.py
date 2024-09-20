from django.db import models

# Create your models here.

class Nosotros(models.Model):
    foto = models.ImageField(null=True, blank=True, upload_to="Fotos_nosotros")
    descripcion=models.CharField(max_length=50, blank=True,null=True)
    
    class Meta:
            db_table = "nosotros"
            verbose_name = "Nosotros"
            verbose_name_plural = "Nosotros"

class Permisos(models.Model):
    id_permiso= models.AutoField(primary_key=True, null=False)
    nombre = models.CharField(max_length=20, null=False)
    
    class Meta:
            db_table = "permisos"
            verbose_name = "Permiso"
            verbose_name_plural = "Permisos"
            
            
class Rol(models.Model):
    id_rol= models.AutoField(primary_key=True, null=False)
    nombre = models.CharField(max_length=20, null=False)
    permiso = models.ManyToManyField(Permisos, through="Rol_permiso")
    
    class Meta:
            db_table = "rol"
            verbose_name="Rol"
            verbose_name_plural = "Roles"

class Rol_permiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permisos, on_delete=models.CASCADE)
    
    class Meta:
            db_table = "rol_permiso"
            verbose_name = "Rol_Permiso"
            verbose_name_plural = "Roles_Permisos"
