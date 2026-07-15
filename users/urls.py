from django.urls import include, path
from . import views

urlpatterns = [
        path('usuarios/', views.registrar_usuario, name='usuarios'),
        path('registro_usuarios/', views.registrar_usuario , name="registro_usuarios"),
        
        #Urls para los empleados,  registrar, editar y listar
        path('empleados/', views.listar_empleados, name='empleados'),
        path('editar_empleados/<str:id>/',views.editar_empleados,name="editar_empleados"),
        path('registrar_empleados/', views.registrar_empleados, name="registrar_empleados"),
        path('cambiar_estado/<int:id>', views.cambiar_estado, name="cambiar_estado"),

        #Urls para la gestión de tareas
        path('tareas/', views.gestion_tareas, name='gestion_tareas'),
        path('completar_tarea/<int:id_tarea>/', views.completar_tarea, name='completar_tarea'),
        path('reactivar_tarea/<int:id_tarea>/', views.reactivar_tarea, name='reactivar_tarea'),
        path('eliminar_tarea/<int:id_tarea>/', views.eliminar_tarea, name='eliminar_tarea'),

        #Urls para la agenda y gestión de cursos
        path('agenda/', views.agenda_personal, name='agenda_personal'),
        path('subir_certificado/<int:id_empleado_curso>/', views.subir_certificado, name='subir_certificado'),
        path('eliminar_certificado/<int:id_empleado_curso>/', views.eliminar_certificado, name='eliminar_certificado'),
        path('gestion_cursos/', views.gestion_cursos, name='gestion_cursos'),
        path('validar_certificado/<int:id_empleado_curso>/', views.validar_certificado, name='validar_certificado'),
        path('soporte_empleado/', views.soporte_empleado, name='soporte_empleado'),

        path('editar_curso/<int:id_curso>/', views.editar_curso, name='editar_curso'),
        path('eliminar_curso/<int:id_curso>/', views.eliminar_curso, name='eliminar_curso'),
        #Urls de perfiles por rol
        path('perfil_empleado/', views.perfil_empleado, name='perfil_empleado'),
        path('perfil_admin/', views.perfil_admin, name='perfil_admin'),
        # URLs de Supervisión y Reportes para Admin
        path('ver_agenda/<int:empleado_id>/', views.ver_agenda_empleado, name='ver_agenda_empleado'),
        path('exportar_matriz/', views.exportar_matriz_excel, name='exportar_matriz_excel'),
        
        # URLs para descarga de PDFs
        path('descargar_pdf_empleados/', views.descargar_pdf_empleados, name='descargar_pdf_empleados'),
        path('descargar_pdf_usuarios/', views.descargar_pdf_usuarios, name='descargar_pdf_usuarios'),
        path('descargar_pdf_cumplimiento/', views.descargar_pdf_cumplimiento, name='descargar_pdf_cumplimiento'),

        # Nuevas funcionalidades de gestión de usuarios
        path('cambiar_estado_usuario/<int:id>/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
        path('editar_usuario_rapido/<int:id>/', views.editar_usuario_rapido, name='editar_usuario_rapido'),
        path('reset_password_usuario/<int:id>/', views.reset_password_usuario, name='reset_password_usuario'),
        path('exportar_usuarios/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),

        # Nuevas funcionalidades de gestión de empleados
        path('exportar_empleados/', views.exportar_empleados_excel, name='exportar_empleados_excel'),
        path('asignar_curso_empleado/<int:id_empleado>/', views.asignar_curso_empleado, name='asignar_curso_empleado'),
        path('enviar_notificacion_empleado/<int:id_empleado>/', views.enviar_notificacion_empleado, name='enviar_notificacion_empleado'),
        path('crear_tarea_rapida_empleado/<int:id_empleado>/', views.crear_tarea_rapida_empleado, name='crear_tarea_rapida_empleado'),
        path('notificar_vencimiento_masivo/', views.notificar_vencimiento_masivo, name='notificar_vencimiento_masivo'),
        
        # Nuevas Integraciones
        path('api/chat/', views.chat_api, name='chat_api'),
        path('auditoria/', views.panel_auditoria, name='panel_auditoria'),
        path('reporte_rrhh/', views.reporte_rrhh, name='reporte_rrhh'),

        # URLs de PQRS y Cotizaciones
        path('gestion-pqrs/', views.gestion_pqrs, name='gestion_pqrs'),
        path('responder-pqrs/<int:id_pqr>/', views.responder_pqrs, name='responder_pqrs'),
        path('gestion-cotizaciones/', views.gestion_cotizaciones, name='gestion_cotizaciones'),

        # URLs de Inventario
        path('inventario/', views.gestion_inventario, name='gestion_inventario'),
        path('inventario/lista/', views.gestion_inventario, name='new_inventory_list'), # Alias para evitar errores de reversión
        path('inventario/importar/', views.importar_inventario_excel, name='importar_inventario_excel'),
        path('inventario/crear/', views.crear_item_inventario, name='crear_item_inventario'),
        path('inventario/editar/<int:pk>/', views.editar_equipo_inventario, name='editar_equipo_inventario'),
        path('inventario/bases/crear/', views.crear_base, name='crear_base'),
        path('inventario/bases/editar/<int:pk>/', views.editar_base, name='editar_base'),
        path('inventario/bases/eliminar/<int:pk>/', views.eliminar_base, name='eliminar_base'),
        path('inventario/proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
        path('inventario/proyectos/editar/<int:pk>/', views.editar_proyecto, name='editar_proyecto'),
        path('inventario/proyectos/eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
        path('inventario/proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
        path('inventario/proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
        path('inventario/proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
        path('inventario/exportar/excel/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
        path('inventario/exportar/pdf/', views.descargar_pdf_inventario_general, name='descargar_pdf_inventario_general'),
        path('inventario/movimientos/exportar/', views.exportar_movimientos_excel, name='exportar_movimientos_excel'),
        path('inventario/eliminar/<int:pk>/', views.eliminar_equipo_inventario, name='eliminar_equipo_inventario'),
        path('inventario/movimiento/', views.new_record_stock_movement, name='new_record_stock_movement'),
        path('inventario/transferir/', views.transferir_item_inventario, name='transferir_item_inventario'),
        path('inventario/solicitar/', views.solicitar_transferencia, name='solicitar_transferencia'),
        path('inventario/procesar/<int:request_id>/', views.procesar_transferencia, name='procesar_transferencia'),
        path('inventario/recibir/<int:request_id>/', views.recibir_transferencia, name='recibir_transferencia'),
        path('inventario/requisicion/pdf/<str:batch_id>/', views.descargar_requisicion_pdf, name='descargar_requisicion_pdf'),
        path('inventario/reset-total/', views.reiniciar_inventario_data, name='reiniciar_inventario_data'),

    ]