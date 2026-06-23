from django.contrib import admin
from .models import (
    Ubicacion, Cargo, Empleado, Tarea, Curso, EmpleadoCurso, LogActividad,
    MensajeChat, InventoryCategory, InventoryItem, StockTransaction,
)

# Register your models here.
admin.site.register(Ubicacion)
admin.site.register(Cargo)
admin.site.register(Empleado)
admin.site.register(Tarea)
admin.site.register(Curso)
admin.site.register(EmpleadoCurso)
admin.site.register(MensajeChat)
admin.site.register(InventoryCategory)
admin.site.register(InventoryItem)
admin.site.register(StockTransaction)
admin.site.register(LogActividad) # Mantener LogActividad registrado
