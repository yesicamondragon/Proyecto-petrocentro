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