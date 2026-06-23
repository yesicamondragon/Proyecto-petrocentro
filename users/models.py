from django.db import models
from paginaPetrocentro.models import Usuario, Estado # Import Estado here as well
from configuracion.models import *
from datetime import timedelta # Import timedelta
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
class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre Corto (Ej: Proyecto 1)")
    observations = models.TextField(blank=True, null=True, verbose_name="Nombre Real / Observaciones (Ej: CHIP)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_project"
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.name

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

# --- NUEVOS MODELOS DE INVENTARIO (Desde Cero) ---

class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        db_table = "inventory_category"
        verbose_name = "Categoría de Inventario"
        verbose_name_plural = "Categorías de Inventario"

    def __str__(self):
        return self.name
class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT/Identificación")
    contacto_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre de Contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "proveedor"
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre

class InventoryItem(models.Model):
    STATUS_CHOICES = [
        ('OPERATIVO', 'OPERATIVO'),
        ('FUERA DE SERVICIO', 'FUERA DE SERVICIO'),
        ('DADO DE BAJA', 'DADO DE BAJA'),
        ('VENDIDO', 'VENDIDO'),
        ('EN PROYECTO', 'EN PROYECTO'),
    ]
    UOM_CHOICES = [
        ('UNIDAD', 'UNIDAD'),
        ('GALONES', 'GALONES'),
        ('BARRILES', 'BARRILES'),
        ('LITROS', 'LITROS'),
        ('METROS', 'METROS'),
        ('PULGADAS', 'PULGADAS'),
        ('PIES', 'PIES'),
    ]
    id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=50, verbose_name="SKU/Código")
    name = models.CharField(max_length=200, verbose_name="Nombre del Equipo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción del Artículo")
    technical_spec = models.TextField(blank=True, null=True, verbose_name="Especificación Técnica")
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, related_name="items", verbose_name="Categoría")
    supplier = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    equipment_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Equipo")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    serial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial")
    tag = models.CharField(max_length=100, blank=True, null=True, verbose_name="TAG")
    owner = models.CharField(max_length=100, blank=True, null=True, verbose_name="Propiedad")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="OPERATIVO", verbose_name="Estado")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Precio Unitario")
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo")
    calibration_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo Calibración")
    length = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Largo (m)")
    width = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ancho (m)")
    height = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Alto (m)")
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Peso (kg)")
    current_stock = models.IntegerField(default=0, verbose_name="Stock Actual")
    rented_quantity = models.IntegerField(default=0, verbose_name="Cantidad Alquilada")
    manufacturing_quantity = models.IntegerField(default=0, verbose_name="Cantidad Fabricando")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proyecto")
    ods_order = models.CharField(max_length=100, blank=True, null=True, verbose_name="Orden ODS")
    calibration_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Calibración")
    maintenance_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Mantenimiento")
    warranty = models.CharField(max_length=100, blank=True, null=True, verbose_name="Garantía")
    min_stock = models.IntegerField(default=5, verbose_name="Stock Mínimo", help_text="Alerta cuando el stock sea menor a este valor")
    max_stock = models.IntegerField(default=100, verbose_name="Stock Máximo", help_text="Capacidad máxima permitida en bodega")
    unit_of_measure = models.CharField(max_length=50, choices=UOM_CHOICES, default="UNIDAD", verbose_name="Unidad de Medida")
    base = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Base/Sede")
    location_detail = models.CharField(max_length=100, blank=True, null=True, verbose_name="Detalle Ubicación", help_text="Ej: Bodega A, Estante 4")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    @property
    def needs_reorder(self):
        return self.current_stock <= self.min_stock

    @property
    def days_operating(self):
        return (timezone.now() - self.created_at).days

    @property
    def needs_calibration(self):
        if self.calibration_date:
            # Alert if calibration is overdue or due within the next 30 days
            return self.calibration_date <= timezone.now().date() + timedelta(days=30)
        return False # No calibration date set, so no alert

    @property
    def needs_maintenance(self):
        if self.maintenance_date:
            # Alerta si el mantenimiento está vencido o vence en los próximos 30 días
            return self.maintenance_date <= timezone.now().date() + timedelta(days=30)
        return False

    @property
    def total_stock_value(self):
        return self.current_stock * self.unit_price

    class Meta:
        db_table = "inventory_item"
        verbose_name = "Equipo de Inventario"
        verbose_name_plural = "Equipos de Inventario"
        unique_together = ('sku', 'base', 'project')

    def __str__(self):
        return f"{self.sku} - {self.name}"

class StockTransaction(models.Model):
    MOVEMENT_TYPES = [
        ('ENTRY', 'Entrada (Compra/Producción)'),
        ('EXIT', 'Salida (Consumo/Baja/Venta)'),
        ('RETURN', 'Devolución (Reingreso)'),
        ('TRANSFER', 'Traslado entre Bases'),
        ('ADJUST_IN', 'Ajuste Positivo (Corrección)'),
        ('ADJUST_OUT', 'Ajuste Negativo (Pérdida/Deterioro)'),
    ]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="transactions", verbose_name="Equipo")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name="Tipo de Movimiento")
    quantity = models.IntegerField(verbose_name="Cantidad")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    responsible = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    reason = models.TextField(blank=True, null=True, verbose_name="Motivo")
    origin_base = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_out", verbose_name="Base Origen")
    destination_base = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_in", verbose_name="Base Destino")
    origin_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_transfers_out", verbose_name="Proyecto Origen")
    destination_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_transfers_in", verbose_name="Proyecto Destino")

    class Meta:
        db_table = "stock_transaction"
        verbose_name = "Transacción de Stock"
        verbose_name_plural = "Transacciones de Stock"
        ordering = ['-date']

    def __str__(self):
        return f"{self.movement_type} {self.quantity} de {self.item.name} por {self.responsible.nombre if self.responsible else 'N/A'}"

class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('SENT', 'Enviado'),
        ('COMPLETED', 'Completado'),
        ('REJECTED', 'Rechazado'),
    ]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, verbose_name="Equipo")
    destination_base = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, verbose_name="Base Destino", null=True, blank=True)
    destination_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proyecto Destino")
    quantity = models.IntegerField(verbose_name="Cantidad")
    supervisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="requests_made", verbose_name="Supervisor Solicitante")
    reason = models.TextField(blank=True, null=True, verbose_name="Motivo del Traslado")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests_processed", verbose_name="Procesado por (Admin)")
    processed_at = models.DateTimeField(null=True, blank=True)
    received_quantity = models.IntegerField(null=True, blank=True, verbose_name="Cantidad Recibida")
    incidents = models.TextField(blank=True, null=True, verbose_name="Novedades de Entrega")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Notas del Administrador/Motivo")
    batch_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID de Lote")
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "transfer_request"
        verbose_name = "Solicitud de Traslado"
        verbose_name_plural = "Solicitudes de Traslado"

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
