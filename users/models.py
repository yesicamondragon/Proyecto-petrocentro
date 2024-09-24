from django.db import models
from paginaPetrocentro.models import Usuario
from configuracion.models import *
class Ubicacion(models.Model):
    idUbicacion= models.AutoField(primary_key=True, null=False)
    nombre = models.CharField(max_length=20, null=False)
    
    class Meta:
            db_table = "ubicacion"
            verbose_name = 'Ubicación'
            verbose_name_plural = 'Ubicaciones'
    
    def __str__(self):
        return self.nombre


    
class Cargo(models.Model):
    id_cargo= models.AutoField(primary_key=True, null=False)
    nombre = models.CharField(max_length=20, null=False)
    
    class Meta:
            db_table = "cargo"
            verbose_name = 'Cargo'
            verbose_name_plural = 'Cargos'
            

# Create your models here.
class Empleado(Usuario):
        
        identificacion = models.IntegerField(null=False )
        telefono = models.CharField(max_length=10, null=False)
        id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
        fecha_ingreso= models.DateField()
        id_cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
        id_ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    
        class Meta:
                db_table = "empleado"
                ordering=['nombre']
                verbose_name = 'Empleado'
                verbose_name_plural = 'Empleados'
