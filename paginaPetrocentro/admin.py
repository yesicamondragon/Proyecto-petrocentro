from django.contrib import admin
from .models import ChatMessage, Usuario, Estado, PQRS, Cotizacion
from users.models import Candidato
from django.core.mail import send_mail
from Petrocentro import settings

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Estado)

@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    list_display = ('radicado', 'nombre', 'tipo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'tipo', 'fecha_creacion')
    search_fields = ('radicado', 'nombre', 'correo')
    readonly_fields = ('radicado', 'fecha_creacion')
    list_editable = ('estado',)
    
    def save_model(self, request, obj, form, change):
        if change:
            # Obtenemos la instancia previa de la base de datos para comparar cambios
            try:
                old_obj = PQRS.objects.get(pk=obj.pk)
            except PQRS.DoesNotExist:
                old_obj = None

            # Si se redacta una respuesta y el estado seguía como 'Pendiente', 
            # lo marcamos como 'Resuelto' automáticamente por conveniencia.
            if old_obj and not old_obj.respuesta and obj.respuesta and obj.estado == 'Pendiente':
                obj.estado = 'Resuelto'
            
            # Verificamos si debemos notificar al usuario: 
            # 1. El estado actual es 'Resuelto' y hay contenido en la respuesta.
            # 2. El estado acaba de cambiar a 'Resuelto' O el texto de la respuesta ha sido modificado.
            if obj.estado == 'Resuelto' and obj.respuesta:
                status_changed = old_obj and old_obj.estado != 'Resuelto'
                response_updated = old_obj and old_obj.respuesta != obj.respuesta
                
                if status_changed or response_updated:
                    # Enviar correo automático al usuario con la respuesta y link de consulta
                    subject = f"Respuesta a su solicitud - Radicado {obj.radicado}"
                    message = f"Hola {obj.nombre},\n\nPetrocentro ha respondido a su {obj.tipo}:\n\n{obj.respuesta}\n\nPuede consultar el historial completo aquí: {settings.DOMAIN_NAME}/consultar-pqrs/?radicado={obj.radicado}"
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [obj.correo], fail_silently=True)

        super().save_model(request, obj, form, change)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'message', 'timestamp', 'is_support')
    list_filter = ('is_support', 'timestamp')
    search_fields = ('message', 'sender_name')

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'servicio', 'email', 'telefono', 'fecha_creacion')
    list_filter = ('servicio', 'fecha_creacion')
    search_fields = ('nombre', 'empresa', 'email', 'mensaje')
    readonly_fields = ('fecha_creacion',)

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'cargo_interes', 'fecha_postulacion')
    list_filter = ('cargo_interes', 'fecha_postulacion')
    search_fields = ('nombre', 'correo')
    readonly_fields = ('fecha_postulacion',)
