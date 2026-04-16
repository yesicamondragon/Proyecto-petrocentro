
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=100) # Nombre del visitante o Agente/Bot
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_support = models.BooleanField(default=False) # True si lo envió Soporte o el Bot

    class Meta:
        db_table = "chat_message"
        ordering = ['timestamp']
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"

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

class Suscriptores(models.Model):
    correo = models.EmailField(max_length=100, unique=True)
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suscriptores"
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"

    def __str__(self):
        return self.correo

class PQRS(models.Model):
    TIPOS = [
        ('Peticion', 'Petición'),
        ('Queja', 'Queja'),
        ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'),
    ]
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelto', 'Resuelto'),
    ]
    
    radicado = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    respuesta = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.radicado:
            import random
            import string
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.radicado = f"PQR-{date_str}-{random_str}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "pqrs_solicitudes"
        verbose_name = "PQRS"
        verbose_name_plural = "PQRS"

class Valoracion(models.Model):
    servicio = models.CharField(max_length=100)
    puntuacion = models.IntegerField()
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    comentario_texto = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "valoraciones"
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"

class Cotizacion(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    servicio = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cotizaciones"
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.servicio}"