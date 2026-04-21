from django.db import models
from paginaPetrocentro.models import Usuario
from configuracion.models import *
from django.utils import timezone
from django.core.validators import FileExtensionValidator
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
    nombre = models.CharField(max_length=50, null=False)
    
    class Meta:
            db_table = "cargo"
            verbose_name = 'Cargo'
            verbose_name_plural = 'Cargos'
            

# Create your models here.
class Empleado(Usuario):
        
        identificacion = models.IntegerField(null=False )
        telefono = models.CharField(max_length=10, null=False)
        id_rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
        fecha_ingreso= models.DateField()
        id_cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
        id_ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    
        class Meta:
                db_table = "empleado"
                ordering=['nombre']
                verbose_name = 'Empleado'
                verbose_name_plural = 'Empleados'

class Tarea(models.Model):
    id_tarea = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, null=False)
    descripcion = models.TextField(null=True, blank=True)
    fecha_limite = models.DateField(null=False)
    completada = models.BooleanField(default=False)
    archivo_adjunto = models.FileField(upload_to='reportes_tareas/', null=True, blank=True, verbose_name="Archivo Adjunto")
    comentarios_cumplimiento = models.TextField(null=True, blank=True, verbose_name="Comentarios de cumplimiento")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # La tarea se asigna a un CARGO, definiendo la tarea concreta para ese rol profesional
    id_cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, verbose_name="Cargo Responsable", null=True, blank=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado Asignado", null=True, blank=True)

    @property
    def is_overdue(self):
        # Retorna True si la tarea no está completada y la fecha límite es anterior a hoy
        return not self.completada and self.fecha_limite < timezone.now().date()

    class Meta:
        db_table = "tarea"
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

class Curso(models.Model):
    MODALIDAD_CHOICES = [
        ('VIRTUAL', 'Virtual'),
        ('PRESENCIAL', 'Presencial'),
    ]
    PERIODICIDAD_CHOICES = [
        ('UNICO', 'Único (Una sola vez)'),
        ('ANUAL', 'Anual (Cada año)'),
        ('SEMESTRAL', 'Semestral (Cada 6 meses)'),
        ('MENSUAL', 'Mensual (Cada mes)'),
    ]
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    modalidad = models.CharField(max_length=10, choices=MODALIDAD_CHOICES, default='VIRTUAL', verbose_name="Modalidad")
    periodicidad = models.CharField(max_length=20, choices=PERIODICIDAD_CHOICES, default='UNICO', verbose_name="Periodicidad")
    external_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="URL Externa del Curso")
    lugar = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lugar (Solo Presencial)")
    # Un curso puede ser obligatorio para múltiples cargos
    obligatorio_para = models.ManyToManyField(Cargo, blank=True, related_name="cursos_requeridos")
    
    class Meta:
        db_table = "curso"
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.nombre

class EmpleadoCurso(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    id_empleado_curso = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="cursos_asignados")
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    certificado = models.FileField(upload_to='certificados_cursos/', null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text="Fecha en que el certificado expira.")
    comentarios_revision = models.TextField(blank=True, null=True, help_text="Comentarios del administrador en caso de rechazo.")

    class Meta:
        db_table = "empleado_curso"
        unique_together = ('empleado', 'curso') # Un empleado solo puede tener una entrada por curso
        verbose_name = "Curso de Empleado"
        verbose_name_plural = "Cursos de Empleados"

class LogActividad(models.Model):
    id_log = models.AutoField(primary_key=True)
    usuario_afectado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='logs_afectado', null=True, blank=True)
    admin_responsable = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='logs_responsable')
    accion = models.CharField(max_length=100)
    detalles = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "log_actividad"
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"

class MensajeChat(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes")
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    es_respuesta_admin = models.BooleanField(default=False) # True si lo escribió un admin/soporte

    class Meta:
        db_table = "mensaje_chat"
        ordering = ['fecha']

class Candidato(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    correo = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    cargo_interes = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, verbose_name="Cargo de interés")
    hoja_de_vida = models.FileField(
        upload_to='cvs/', 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Adjunte su hoja de vida solo en formato PDF"
    )
    mensaje = models.TextField(blank=True, null=True, verbose_name="Mensaje/Presentación")
    fecha_postulacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "candidato"
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
