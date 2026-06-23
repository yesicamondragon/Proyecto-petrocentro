// Funciones para mostrar/ocultar el loader (asumiendo que existen en tu HTML o en otro script)
function mostrarLoader() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.style.display = 'flex';
    }
}

function ocultarLoader() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Ejemplo de cómo integrar el loader en una llamada fetch
async function fetchDataAndRenderTable(url, params = {}) {
    mostrarLoader(); // Mostrar el loader antes de la petición
    try {
        const response = await fetch(url + '?' + new URLSearchParams(params));
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Aquí llamarías a tu función para renderizar la tabla
        // renderTabla(data); 
        console.log("Datos recibidos:", data);
        // Asegúrate de que tu función renderTabla maneje los datos correctamente
        // y que el formato JSON del backend sea el esperado.
    } catch (error) {
        console.error("Error al cargar los datos:", error);
        // Mostrar un mensaje de error al usuario si es necesario
    } finally {
        ocultarLoader(); // Ocultar el loader SIEMPRE, sin importar el resultado
    }
}

// Ejemplo de uso (podrías llamar a esta función cuando se cargue la página,
// al hacer clic en un botón de filtro, etc.)
// document.addEventListener('DOMContentLoaded', () => {
//     fetchDataAndRenderTable('/ruta/a/tu/api/datos/', { buscar: 'ejemplo', estado: '1' });
// });

// Función para ver detalles
function verDetallesEquipo(data) {
    console.log("Detalles del equipo:", data);
    // Aquí deberías abrir el modal de detalles y llenar los campos
    const modal = document.getElementById("modalDetails");
    if (modal) {
        modal.style.display = "block";
        // Ejemplo: document.getElementById("det-project").innerText = data.project;
    }
}

// Función para abrir modal de edición
function abrirModalEditar(data) {
    console.log("Editar equipo:", data);
    const modal = document.getElementById("modalEdit");
    if (modal) {
        modal.style.display = "block";
        // Aquí llenas los inputs del modal con los valores de "data"
        // Ejemplo: document.getElementById("edit-name").value = data.name;
    }
}

// Función para confirmar eliminación
function confirmarEliminacion(id, name) {
    if (confirm(`¿Seguro que quieres eliminar ${name}?`)) {
        // Redirige a la ruta de eliminación en Django
        window.location.href = `/inventario/${id}/eliminar/`;
    }
}
