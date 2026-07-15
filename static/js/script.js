// Agregar evento de hover al botón
function cambiarColor(idPath, color, h1Class) {

    var path = document.getElementById(idPath);
    var ubicacion = document.querySelector('.' + h1Class);
    // Cambiar el color de relleno al especificado cuando se hace hover sobre el botón
    ubicacion.style.transition = 'all 500ms ease-out'
    ubicacion.style.display = 'block';

    path.style.fill = color;
    // Añadir efectos de transición
    path.style.transition = 'all 500ms ease-out';
    // Cambiar el título del path 
    path.title = "SIBATE";
    
    path.style.borderWidth = '10px'
    path.style.borderColor = ' #f0f0f0';
    // Aplicar transformaciones CSS 
    if (color === '#dbc607cc' || color === 'rgba(214, 18, 18, 0.767)' ){

        path.style.transform = 'translateX(-15px)';
      
    }
    else{

        path.style.transform = 'translateY(-15px)';
        
    }

    
    // Cambiar el borde (si es aplicable)
    
};

// Agregar evento de salida de hover al botón
function restaurarColor(idPath, h1Class) {
    var path = document.getElementById(idPath);

    var ubicacion = document.querySelector('.' + h1Class);

    ubicacion.style.display = 'none';
    // Restaurar el color de relleno original cuando se sale del hover sobre el botón
    path.style.fill = '#228B22';
    // Añadir efectos de transición
    path.style.transition = 'all 500ms ease-out';
    // Restaurar las transformaciones CSS 
    path.style.transform = 'translateY(0px)';
};

window.onclick = function(event) {
  var modal = document.getElementById("modal");
  if (event.target == modal) {
    modal.style.display = "block";
  }
}

//Lee si el usuario pulso ESC en el teclado para cerrar el modal
window.onkeyup = function(event) {
  var modal = document.getElementById("modal");
  if (event.key === "Escape") {
    modal.style.display = "none";
  }
}

//modales
function showModal(titulo, contenido, imagenUrl) {
    // Atributos del modal
    document.getElementById("modal-titulo").innerText= titulo;
    document.getElementById("modal-contenido").innerText = contenido;
    var modalImagen = document.getElementById("modal-imagen");
    modalImagen.src = imagenUrl;
    modalImagen.style.display = "block";
    document.getElementById("modal").style.display = "block";
  }
  
  //Cerrar el modal
  function closeModal() {
    document.getElementById("modal").style.display = "none";
  }

  //Lee si el usuario pulsa por fuera del area que ocupa el modal para cerrar

  //overlay
document.addEventListener("DOMContentLoaded", function() {
    // Ocultar el elemento de carga cuando la página se haya cargado completamente
    var loadingOverlay = document.getElementById("loadingOverlay");
        loadingOverlay.style.display = "none";

  });
  
  //overlay
  document.addEventListener("DOMContentLoaded", function() {
    // Ocultar el elemento de carga cuando la página se haya cargado completamente
    var loadingOverlay = document.getElementById("loadingOverlay");
        loadingOverlay.style.display = "none";

  });

//Funcion para desplegar el menu de opciones del perfil
function perfil(){
  document.getElementById("lista-perfil").classList.toggle("active-perfil");
}
window.onkeyup = function(e){
  var perfil = document.getElementById("lista-perfil");
  if (e.key === "Escape") {
    perfil.classList.remove("active-perfil");
  }
}
window.onclick = function(e){
  var perfil = document.getElementById("lista-perfil");
  if (e.target == perfil) {
    perfil.classList.toggle("active-perfil");
  }
}
function toggleSidebar(){
  document.getElementById("sidebar").classList.toggle("active-sidebar");
}

function setupPasswordHelpers() {
  const passwordInputs = Array.from(document.querySelectorAll('input[type="password"]'));
  passwordInputs.forEach(input => {
    if (input.dataset.passwordToggleAttached) return;
    const existingWrapper = input.closest('.password-input-wrapper');
    let toggleBtn = existingWrapper ? existingWrapper.querySelector('.password-toggle') : null;
    if (existingWrapper) {
      input.dataset.passwordToggleAttached = '1';
      if (toggleBtn && !toggleBtn.dataset.passwordToggleAttached) {
        toggleBtn.dataset.passwordToggleAttached = '1';
        toggleBtn.addEventListener('click', function(event) {
          event.preventDefault();
          const icon = this.querySelector('i');
          if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'fa-solid fa-eye-slash';
          } else {
            input.type = 'password';
            icon.className = 'fa-solid fa-eye';
          }
        });
      }
      return;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'password-input-wrapper';
    const parent = input.parentNode;
    parent.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.width = '100%';
    input.style.paddingRight = '3rem';

    toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'password-toggle';
    toggleBtn.title = 'Mostrar / Ocultar contraseña';
    toggleBtn.style.position = 'absolute';
    toggleBtn.style.top = '50%';
    toggleBtn.style.right = '0.75rem';
    toggleBtn.style.transform = 'translateY(-50%)';
    toggleBtn.style.border = 'none';
    toggleBtn.style.background = 'transparent';
    toggleBtn.style.padding = '0.25rem';
    toggleBtn.style.cursor = 'pointer';
    toggleBtn.style.zIndex = '2';
    toggleBtn.innerHTML = '<i class="fa-solid fa-eye"></i>';
    wrapper.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', function(event) {
      event.preventDefault();
      const icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fa-solid fa-eye-slash';
      } else {
        input.type = 'password';
        icon.className = 'fa-solid fa-eye';
      }
    });

    input.dataset.passwordToggleAttached = '1';
  });

  document.querySelectorAll('form').forEach(form => {
    const passwordFields = Array.from(form.querySelectorAll('input[type="password"]'));
    if (passwordFields.length < 2) return;

    const confirmFields = passwordFields.filter(field => /confirm|repeat|again|verif|repetir|2$|new_password2|new-password2/i.test(field.name + ' ' + field.id));
    confirmFields.forEach(confirmInput => {
      const possibleOriginals = passwordFields.filter(field => field !== confirmInput && !/confirm|repeat|again|verif|repetir|2$|new_password2|new-password2/i.test(field.name + ' ' + field.id));
      const originalInput = possibleOriginals.length === 1 ? possibleOriginals[0] : passwordFields.find(field => field !== confirmInput);
      if (!originalInput) return;

      const status = document.createElement('div');
      status.className = 'password-match-status';
      confirmInput.parentNode.insertBefore(status, confirmInput.nextSibling);

      const updateStatus = () => {
        if (!confirmInput.value && !originalInput.value) {
          status.textContent = '';
          confirmInput.setCustomValidity('');
          return;
        }
        if (confirmInput.value === originalInput.value) {
          status.textContent = 'Las contraseñas coinciden.';
          status.style.color = '#198754';
          confirmInput.setCustomValidity('');
        } else {
          status.textContent = 'Las contraseñas no coinciden.';
          status.style.color = '#dc3545';
          confirmInput.setCustomValidity('Las contraseñas deben coincidir.');
        }
      };

      originalInput.addEventListener('input', updateStatus);
      confirmInput.addEventListener('input', updateStatus);

      form.addEventListener('submit', event => {
        if (originalInput.value && confirmInput.value && originalInput.value !== confirmInput.value) {
          event.preventDefault();
          updateStatus();
          confirmInput.focus();
        }
      });
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  setupPasswordHelpers();
});

document.addEventListener('click', function(event) {
  const toggleBtn = event.target.closest('.password-toggle');
  if (!toggleBtn) return;
  event.preventDefault();
  const wrapper = toggleBtn.closest('.password-input-wrapper');
  if (!wrapper) return;
  const input = wrapper.querySelector('input[type="password"], input[type="text"]');
  if (!input) return;
  const icon = toggleBtn.querySelector('i');
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) icon.className = 'fa-solid fa-eye-slash';
  } else {
    input.type = 'password';
    if (icon) icon.className = 'fa-solid fa-eye';
  }
});
