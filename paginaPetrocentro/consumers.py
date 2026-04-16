import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Creamos un grupo de chat general (para soporte o global)
        self.room_group_name = 'chat_general'

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, user, sender_name, message, is_support):
        # Manejo seguro para usuarios anónimos (Visitantes)
        user_instance = user if user and user.is_authenticated else None
        return ChatMessage.objects.create(
            user=user_instance,
            sender_name=sender_name,
            message=message,
            is_support=is_support
        )

    # Recibir mensaje del WebSocket (Frontend)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope.get('user') # Usar .get() para evitar errores si no está configurado el AuthMiddleware

        # Identificar rol: Si está logueado es Soporte, si no es Visitante
        if user and user.is_authenticated:
            sender_type = 'support'
            display_name = f"Agente {user.first_name or user.username}"
        else:
            sender_type = 'visitor'
            display_name = "Visitante"

        # Guardar el mensaje del usuario en la base de datos
        await self.save_message(user, display_name, message, sender_type == 'support')

        # Enviar mensaje al grupo (Backend -> Grupo)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', 
                'message': message,
                'sender_type': sender_type,
                'name': display_name,
                'origin_channel': self.channel_name # Para saber quién lo envió
            }
        )
        
        # --- Lógica del Bot (Modificado para responder a todos) ---
        response = None
        msg_lower = message.lower()
        
        # --- Respuestas Automáticas ---
        if any(word in msg_lower for word in ["hola", "buenos", "buenas", "inicio"]):
            response = "¡Hola! Bienvenido a Petrocentro. 👋<br>Puedo ayudarte con información sobre:<br>🔹 <b>Horarios</b><br>🔹 <b>Ubicación</b><br>🔹 <b>Precios/Cotizaciones</b><br>🔹 <b>Facturación</b>"
        elif "horario" in msg_lower:
            response = "🕒 <b>Horario de Atención:</b><br>Lunes a Viernes: 8:30 AM - 5:30 PM.<br>Sábados y Domingos: No hay servicio."
        elif any(word in msg_lower for word in ["ubicacion", "ubicación", "donde", "dónde", "direccion", "dirección", "sede"]):
            response = "📍 <b>Sede Principal:</b><br>Avenida Calle 127 #13-96, Bogotá.<br>También contamos con bases en Meta y Putumayo."
        elif any(word in msg_lower for word in ["precio", "costo", "cotiza", "valor"]):
            response = "💰 <b>Cotizaciones:</b><br>Manejamos tarifas personalizadas.<br>Para una oferta formal, llena nuestro formulario:<br><a href='/contacto/' class='btn btn-sm btn-light border mt-2' style='text-decoration:none; color:#333;' target='_blank'>📝 Ir a Formulario de Cotización</a>"
        elif any(word in msg_lower for word in ["factura", "facturación", "pago", "electronica", "electrónica"]):
            response = "📄 <b>Facturación:</b><br>Para temas administrativos y facturación electrónica, escribe a: <i>ti.petrocentro@gmail.com</i><br>WhatsApp: 3134267179"
        
        # --- Fallback: Redirección a WhatsApp ---
        else:
            response = (
                "Entiendo, para esa consulta específica te recomiendo hablar con un ingeniero especializado.<br><br>"
                "<a href='https://wa.me/573134267179?text=Hola,%20tengo%20una%20consulta%20desde%20la%20web' target='_blank' class='btn btn-success btn-sm' style='color:white; text-decoration:none;'>"
                "<i class='fa fa-whatsapp'></i> Hablar con un Asesor"
                "</a>"
            )

        if response:
            # Guardar la respuesta del bot en la base de datos
            await self.save_message(None, '🤖 Bot Petrocentro', response, True)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message', 
                    'message': response,
                    'sender_type': 'bot',
                    'name': '🤖 Bot Petrocentro',
                    'origin_channel': 'bot_server'
                }
            )

    # Recibir mensaje del grupo (Grupo -> WebSocket)
    async def chat_message(self, event):
        message = event['message']
        sender_type = event['sender_type']
        name = event['name']
        origin_channel = event['origin_channel']
        
        # Determinar si el mensaje lo envié yo mismo
        is_me = (origin_channel == self.channel_name)

        # Enviar mensaje al WebSocket (Frontend)
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_type': sender_type,
            'name': name,
            'is_me': is_me
        }))