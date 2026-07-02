var __subscribeFormEl = document.getElementById('subscribeForm');
if (__subscribeFormEl) {
    __subscribeFormEl.addEventListener('submit', function(e) {
        e.preventDefault();
        var email = document.getElementById('emailInput') ? document.getElementById('emailInput').value : '';
        var messageBox = document.getElementById('messageBox');
  
  // Crear un objeto con los datos del formulario
  var formData = new FormData();
  formData.append('email', email);

  // Enviar la solicitud AJAX
  fetch('/suscribirse/', {
      method: 'POST',
      body: formData,
      headers: {
          'X-CSRFToken': getCookie('csrftoken')  // Asegúrate de incluir el token CSRF
      }
  })
  .then(response => response.json())
  .then(data => {
      if (messageBox) {
          if (data.success) {
              messageBox.textContent = '¡Te has suscrito correctamente!';
              messageBox.className = 'message success';
              if (document.getElementById('emailInput')) document.getElementById('emailInput').value = '';
          } else {
              messageBox.textContent = 'Error: ' + data.error;
              messageBox.className = 'message error';
          }
          messageBox.style.display = 'block';
      }
  })
  .catch(error => {
      console.error('Error:', error);
            if (messageBox) {
                messageBox.textContent = 'Ocurrió un error al procesar tu solicitud.';
                messageBox.className = 'message error';
                messageBox.style.display = 'block';
            }
  });
});
} else {
    console.debug('subscribeForm no presente — suscribeForm.js no ha añadido listeners.');
}

// Función para obtener el token CSRF de las cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


