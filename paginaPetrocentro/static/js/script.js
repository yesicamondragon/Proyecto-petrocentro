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
function showModal(titulo, contenido) {

    // Atributos del modal
    document.getElementById("modal-titulo").innerText= titulo;
    document.getElementById("modal-contenido").innerText = contenido;
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