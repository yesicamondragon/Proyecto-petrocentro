# 🔧 Guía de Configuración ASGI para WebSockets - Petrocentro

## 📋 Resumen de Cambios Realizados

Se han corregido 3 problemas principales en tu proyecto:

### ✅ 1. jQuery Corrupto → Reemplazado con CDN
- **Problema:** `jquery-1.11.3.min.js` estaba corrupto
- **Error:** "Uncaught SyntaxError: Unexpected identifier 'm'"
- **Solución:** Cambiado a jQuery 3.6 desde CDN oficial

### ✅ 2. Orden de Carga de Scripts Incorrecto
- **Problema:** script.js y whatsapp-chat-support.js se cargaban ANTES de jQuery
- **Errores:** "jQuery is not defined", "$ is not defined"
- **Solución:** jQuery ahora carga primero, luego plugins que lo requieren

### ✅ 3. Manejo de Errores WebSocket Mejorado
- **Cambio:** Agregado `chatSocket.onerror` para diagnosticar problemas
- **Beneficio:** Mensajes de error más claros en consola del navegador

---

## 🚀 Paso 1: Instalar Dependencias ASGI

Asegúrate de tener las dependencias instaladas en tu virtualenv:

```bash
# Activa tu virtualenv
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate

# Instala daphne (servidor ASGI)
pip install daphne

# Verifica que channels ya está instalado
pip list | grep -i channels
```

---

## 🏃 Paso 2: Ejecutar Servidor con ASGI

### Opción A: Desarrollo Local (RECOMENDADO)

Usa **Daphne** para ejecutar con soporte WebSocket:

```bash
daphne -b 0.0.0.0 -p 8000 Petrocentro.asgi:application
```

**Flags explicados:**
- `-b 0.0.0.0`: Vincularse a todas las interfaces de red
- `-p 8000`: Puerto 8000 (cambia si es necesario)
- `Petrocentro.asgi:application`: Ruta a la aplicación ASGI

**Salida esperada:**
```
2024-06-25 14:30:00,000 daphne.server INFO Listening on TCP address 0.0.0.0:8000
Starting WebSocket ASGI application...
```

### Opción B: Con Uvicorn (Alternativa)

```bash
pip install uvicorn
uvicorn Petrocentro.asgi:application --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ Paso 3: Verificar que WebSocket Funciona

1. **Abre tu navegador** en http://localhost:8000 (o tu URL)
2. **Abre Developer Tools** (F12 en Windows/Linux, Cmd+Option+I en Mac)
3. **Ir a la pestaña Console**
4. **Baja a la esquina inferior derecha** y haz clic en el botón de chat (comentarios 💬)
5. **Verifica el estado:**
   - ✅ **Verde "En línea"** → WebSocket conectado correctamente
   - ❌ **Rojo "Desconectado"** → Servidor NO está en ASGI

**En la Consola deberías ver:**
```javascript
Chat conectado correctamente  // ✅ Si funciona
// O
Error WebSocket: DOMException  // ❌ Si hay problema
```

---

## 🌐 Producción (Render, PythonAnywhere, etc.)

### En Render.com

1. **Crear nuevo `Procfile`** en la raíz del proyecto:
```
web: daphne -b 0.0.0.0 -p $PORT Petrocentro.asgi:application
```

2. **Asegúrate que `channels` está en `requirements.txt`:**
```
daphne==4.0.0
channels==4.0.0
channels-redis==4.1.0  # Para producción
```

3. **Deploy:** Hacer commit y push a GitHub

### En PythonAnywhere

1. **Cargar archivos** via SFTP o git
2. **En Web > Add new web app:**
   - Selecciona Python (tu versión)
   - **NO selecciones Django** - selecciona "Manual configuration"
3. **WSGI configuration file:** Edita y reemplaza con:
```python
import os
import sys
from daphne.cli import CommandLineInterface

os.environ['DJANGO_SETTINGS_MODULE'] = 'Petrocentro.settings'
os.chdir('/home/usuario/Petrocentro')
sys.path.insert(0, '/home/usuario/Petrocentro')

application = CommandLineInterface(sys.argv).application
```

---

## 🔍 Diagnóstico: ¿Por qué no conecta WebSocket?

### 1. Comprueba que Daphne está corriendo
```bash
# En otra terminal, prueba:
curl -i http://localhost:8000/
```

Debería responder, no "Connection refused"

### 2. Revisa la consola del servidor
```
- ERROR: Si ves "Connection refused" en el navegador
- SOLUCIÓN: El servidor no está activo o en otro puerto
```

### 3. Mira los logs en Dev Tools (F12)
```javascript
// Abre Console y busca:
"WebSocket connection to 'wss://...' failed"
// Si lo ves, el server no está escuchando WebSocket
```

### 4. Verifica HTTPS
- En HTTPS → usa `wss://` (WebSocket Secure)
- En HTTP → usa `ws://` (WebSocket)
- El código detecta automáticamente: ✅

---

## 📦 Checklist de Verificación

- [ ] Instalaste `daphne` con `pip install daphne`
- [ ] Ejecutas con `daphne -b 0.0.0.0 -p 8000 Petrocentro.asgi:application`
- [ ] La página carga sin errores de jQuery
- [ ] El chat muestra "En línea" en verde
- [ ] Puedes ver en DevTools: "Chat conectado correctamente"

---

## 🐛 Si Sigue Sin Funcionar

1. **Verifica que Django puede cargar:**
```bash
python manage.py shell
```

2. **Prueba el consumer directamente:**
```bash
python manage.py runserver
# Abre: http://localhost:8000/
# F12 Console → Verifica errores
```

3. **Mira los logs completos:**
```bash
# En Windows
daphne -b 0.0.0.0 -p 8000 -v 3 Petrocentro.asgi:application

# En Linux/Mac
DJANGO_LOG_LEVEL=DEBUG daphne -b 0.0.0.0 -p 8000 Petrocentro.asgi:application
```

---

## 📚 Recursos Útiles

- [Documentación Channels](https://channels.readthedocs.io/)
- [Documentación Daphne](https://github.com/django/daphne)
- [WebSocket API MDN](https://developer.mozilla.org/es/docs/Web/API/WebSocket)

---

## 🎯 ¿Qué sucede ahora?

1. **jQuery:** ✅ Funciona desde CDN
2. **Scripts:** ✅ Cargados en orden correcto
3. **WebSocket:** ⏳ Requiere ejecutar con ASGI (Daphne/Uvicorn)

**El próximo paso es ejecutar tu servidor con Daphne en lugar de `runserver`.**

¿Preguntas? Revisa los logs en la consola del navegador (F12 > Console).
