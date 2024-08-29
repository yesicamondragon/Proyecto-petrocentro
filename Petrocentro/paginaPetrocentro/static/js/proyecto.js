                
// Funcion asíncrona para obtener la cantidad de los items selccionados y así tener un mejor control de las cantidades propuestas
const  obtener_cantidad = async (id) => {
        const csrfTokenValue = document.querySelector(
                "[name=csrfmiddlewaretoken]"
                ).value;
                const headers = {
                "X-CSRFToken": csrfTokenValue,
                };
                
                let url = "/filtrar_cantidad_suministros/";
        try {
                const response = await axios.post(url, { id }, { headers });

                const cantidad = document.getElementById('cantidad_item')
                const { data, status } = response;
                data.data.forEach (item => {
                        cantidad.value = item.cantidad
                
                })
                
        } catch (error) {
                console.log("Error en la petición", error);
        }
}

const  cantidad = async (id,qty,nombre,categoria,ubicacion) => {
        const csrfTokenValue = document.querySelector(
                "[name=csrfmiddlewaretoken]"
                ).value;
                const headers = {
                "X-CSRFToken": csrfTokenValue,
                };
                
                var url = "/filtrar_cantidad_suministros/";
        try {
                const response = await axios.post(url, { id }, { headers });
                const { data, status } = response;

                let cantidad_retornada= ' ';
                data.data.forEach(item => {
                        
                        let resultado = item.cantidad - qty                           
                        if (resultado < 0 ){
                                Swal.fire({
                                        title: 'Error!',
                                        text: '¡Verifica la cantidad!, No se puede agregar.',
                                        icon: 'error',
                                        confirmButtonText: 'Ok.'
                                        })
                                cantidad_retornada = 1
                     
                        }  else if(qty <= 0){
                                console.log('entra aqui')
                                Swal.fire({
                                        title: 'Error!',
                                        text: 'No se puede agregar una cantidad negativa!.',
                                        icon: 'error',
                                        confirmButtonText: 'Ok.'
                                        })
                                cantidad_retornada = 1
                        }
                        else if(nombre && categoria == item.categoria && ubicacion == item.ubicacion ){
                                Swal.fire({
                                        title: 'Error!',
                                        text: 'No se puede agregar, al parecer ya lo agregaste!.',
                                        icon: 'error',
                                        confirmButtonText: 'Ok.'
                                        })
                                cantidad_retornada = 1
                                
                        }else{
                                Swal.fire({
                                        title: 'Success!',
                                        text: 'insumo agregado correctamente.',
                                        icon: 'success',
                                        showConfirmButton: false,  // Quita el botón de confirmación
                                        timer: 500,
                                        timerProgressBar: true,
                                        })
                                        
                                cantidad_retornada = ` Queda: ${resultado } en stock - ${item.categoria__nombre}`;
                        }
                
                       
                })
                return cantidad_retornada;
                
        } catch (error) {
                console.log("Error en la petición", error);
        }
}

// funcion para añadir los items a la lista
function addItem(listId, itemName, itemQty, dinamic) {
        const list = document.getElementById(listId);
        const item = document.getElementById(itemName).value;
        const nombre = document.getElementById(itemName);
        const dinamicList = document.getElementById(dinamic)


        try{
                
                
                if (itemName == 'suministros' ){
                
                        const quantity = document.getElementById(itemQty).value;
                        let selectValue = nombre.value;
                        let selectedI = nombre.selectedIndex;
                        let selectText = nombre.options[selectedI].text;
                        const location = document.getElementById('ubicacion2').value
                        const category = document.getElementById('categoria2').value
                        const nombreList = document.getElementById(`${category}${selectText}${location}`)

                        if (item && quantity) {
                                
                                cantidad(item, quantity,nombreList,category,location).then(funcion_cantidad=>{
                                        if(funcion_cantidad == 1){
                                                const listItem = document.createElement('li');
                                                listItem.textContent = `${selectText}  -${funcion_cantidad} `;
                                   
                                        }
                                        else{
                                                
                                                const listItem = document.createElement('li');
                                                listItem.id=`${category}${selectText}${location}`
                                                listItem.textContent = `${selectText} - Cantidad: ${quantity} - ${funcion_cantidad} `;
        
                                        
                                                dinamicList.appendChild(listItem);    
                                                
                                                const deleteButton = document.createElement('button');
                                                deleteButton.style.color = 'red';
                                                deleteButton.style.cursor = 'pointer';
                                                deleteButton.style.border = 'none'
                                                deleteButton.style.background = 'none';
                                                deleteButton.style.outline = 'none';
                                                deleteButton.style.fontSize = '1.5rem';
                                                deleteButton.type = 'button';
                                                deleteButton.title = 'Eliminar';
                                                deleteButton.id = item; // Evita que el botón envíe el formulario
                                                deleteButton.addEventListener('click', function() {
                                                eliminarItem(hiddenItem,listItem, hiddenQty);
                                                });
        
                                                let icon = document.createElement('i');
                                                icon.classList.add('fa-solid', 'fa-delete-left'); // Usar clases Font Awesome
                                                deleteButton.appendChild(icon);
                                                listItem.appendChild(deleteButton);
        
                                                // Crear inputs invisibles para generar el envío a la vista de
                                                const hiddenItem = document.createElement('input');
                                                hiddenItem.type = 'hidden';
                                                hiddenItem.name = `${itemName}[]`;
                                                hiddenItem.value = item;
                                                list.appendChild(hiddenItem);
        
                                                const hiddenQty = document.createElement('input');
                                                hiddenQty.type = 'hidden';
                                                hiddenQty.name = `${itemQty}[]`;
                                                hiddenQty.value = quantity;
                                                list.appendChild(hiddenQty);
                                                
                                                const cantidad = document.getElementById('cantidad_item').value=""
                                                document.getElementById(itemName).value = '';
                                                document.getElementById(itemQty).value = '';
                                                        
                                       
                                                
                                        }
                                })
                                

                        }
                }else{
                        let selectValue = nombre.value;
                        let selectedI = nombre.selectedIndex;
                        let selectText = nombre.options[selectedI].text;
                        const nombreList = document.getElementById(`${selectText}`)
                        if (item) {
                                if(nombreList){
                                        Swal.fire({
                                                title: 'Error!',
                                                text: 'Este item ya fue agregado, elimina y vuelva a agregar.',
                                                icon: 'error',
                                                confirmButtonText: 'Cool'
                                        })
                                }  
                                
                                else{
                                        const cate = document.getElementById('categoria1')        
                                        console.log(cate)
                                        Swal.fire({
                                                title: 'Success!',
                                                text: 'insumo agregado correctamente.',
                                                icon: 'success',
                                                showConfirmButton: false,  // Quita el botón de confirmación
                                                timer: 500,
                                                timerProgressBar: true,
                                                })
                                        const listItem = document.createElement('li');
                        
                                        listItem.textContent = `${selectText} `;
                                        listItem.id = `${selectText}`;
                                        dinamicList.appendChild(listItem);
                                        
                                        

                                        
                                        const deleteButton = document.createElement('button');
                                        deleteButton.style.color = 'red';
                                        deleteButton.style.cursor = 'pointer';
                                        deleteButton.style.border = 'none'
                                        deleteButton.style.background = 'none';
                                        deleteButton.style.outline = 'none';
                                        deleteButton.style.fontSize = '1.5rem';
                                        deleteButton.type = 'button';
                                        deleteButton.title = 'Eliminar';
                                        deleteButton.id = item; // Evita que el botón envíe el formulario
                                        deleteButton.addEventListener('click', function() {
                                                delete_item(hiddenItem,listItem);
                                        });

                                        let icon = document.createElement('i');
                                        icon.classList.add('fa-solid', 'fa-delete-left'); // Usar clases Font Awesome
                                        deleteButton.appendChild(icon);
                                        listItem.appendChild(deleteButton);

                                        // Crear inputs invisibles para generar el envío a la vista de
                                        const hiddenItem = document.createElement('input');
                                        hiddenItem.type = 'hidden';
                                        hiddenItem.name = `${itemName}[]`;
                                        hiddenItem.value = item;
                                        list.appendChild(hiddenItem);
                                
                                        document.getElementById(itemName).value = '';
                                }                              
                                
                        }
                }
        } catch(error){
                console.log("Error en la petición que acaba de hacer", error);
        }
}    

// Funcion para eliminar algún item de la lista 
function eliminarItem(item, listItem, qty) {

        // Obtener los inputs ocultos dentro del elemento de lista
        item.remove();
        qty.remove();
        // Eliminar el elemento de lista visual
        listItem.remove();
}
function delete_item(item, listItem){
        listItem.remove();
        item.remove();
}

function optionExists(selectElement, valor) {
        let value = ""
        for (let i = 0; i < selectElement.options.length; i++) {
                if (selectElement.options[i].value == valor ){
                        value = true;
                        
                }
        }
        return value
        }

const filtrarCategoriaSuministros= async(ubicacion) =>{
        const csrfTokenValue = document.querySelector(
        "[name=csrfmiddlewaretoken]"
        ).value;
        const headers = {
        "X-CSRFToken": csrfTokenValue,
        };

        let url = "/filtrar_categoria_suministros/";
        try {
        const response = await axios.post(url, { ubicacion }, { headers });

        const { data, status } = response;

        let selectCategoria = document.querySelector("#categoria2");
        selectCategoria.innerHTML = "";
        if (data.data.length == 0) {
                
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "No hay nada aqui";
                selectCategoria.appendChild(defaultOption);
        
        } else {


        // Crea una opción por defecto
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.text = "Seleccione";
        selectCategoria.appendChild(defaultOption);

        // Itera sobre la data para agregar los EQUIPOS al select
        data.data.forEach((item) => {
                
                const option = document.createElement("option");
                const exists = optionExists(selectCategoria, item.categoria);
                
                if(exists){
                        console.log('Ya existe la categoria')
                } else{

                        option.value = item.categoria;
                        option.text = item.categoria__nombre ;
                        selectCategoria.appendChild(option);
                }
        });
        }
        } catch (error) {
        console.log("Error en la petición", error);
        }
}
const filtrarSuministros = async (categoria) => {
        const csrfTokenValue = document.querySelector(
        "[name=csrfmiddlewaretoken]"
        ).value;
        const headers = {
        "X-CSRFToken": csrfTokenValue,
        };
        const selectUbicacion = document.querySelector('#ubicacion2')
        const ubicacion = selectUbicacion.value
        let url = "/filtrar_suministros/";
        try {
                const response = await axios.post(url, { ubicacion, categoria }, { headers });

                const { data, status } = response;
                
                let selectSuministro = document.querySelector("#suministros");
                selectSuministro.innerHTML = "";

                if (data.data.length == 0) {
                        const defaultOption = document.createElement("option");
                        defaultOption.value = "";
                        defaultOption.text = "Stock en 0";
                        selectSuministro.appendChild(defaultOption);
        
                } else {
        

              
        
                // Crea una opción por defecto
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "Seleccione";
                selectSuministro.appendChild(defaultOption);
                
                // Itera sobre la data para agregar los municipios al select
                data.data.forEach((item) => {
                const option = document.createElement("option");
                option.value = item.id;
                option.text =  item.tag;

                selectSuministro.appendChild(option);

                

        });
        }
        } catch (error) {
                console.log("Error en la petición", error);
        }
};

const filtrarCategoriaActivos = async (ubicacion1) =>{
        const csrfTokenValue = document.querySelector(
        "[name=csrfmiddlewaretoken]"
        ).value;
        const headers = {
        "X-CSRFToken": csrfTokenValue,
        };

        let url = "/filtrar_categoria_activos/";
        try {
        const response = await axios.post(url, { ubicacion1 }, { headers });

        const { data, status } = response;

        let selectCategoria = document.querySelector("#categoria1");
        selectCategoria.innerHTML = "";
        if (data.data.length == 0) {
                
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "No hay nada aqui";
                selectCategoria.appendChild(defaultOption);
        
        } else {


        // Crea una opción por defecto
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.text = "Seleccione";
        selectCategoria.appendChild(defaultOption);

        // Itera sobre la data para agregar los EQUIPOS al select
        data.data.forEach((item) => {
                
                const option = document.createElement("option");
                const exists = optionExists(selectCategoria, item.categoria);
                
                if(exists){
                        console.log('Ya existe la categoria')
                } else{

                        option.value = item.categoria;
                        option.text = item.categoria__nombre ;
                        selectCategoria.appendChild(option);
                }
        });
        }
        } catch (error) {
        console.log("Error en la petición", error);
        }
}

const filtrarActivos = async (categoria) => {
        const csrfTokenValue = document.querySelector(
                "[name=csrfmiddlewaretoken]"
                ).value;
                const headers = {
                "X-CSRFToken": csrfTokenValue,
                };
                const selectUbicacion = document.querySelector('#ubicacion1')
                const ubicacion = selectUbicacion.value

                let url = "/filtrar_activos/";
                try {
                const response = await axios.post(url, { categoria, ubicacion }, { headers });
                        
                const { data, status } = response;

                
                let selectActivos = document.querySelector("#activos");
                selectActivos.innerHTML = "";
                if (data.data.length == 0) {
                        
                        const defaultOption = document.createElement("option");
                        defaultOption.value = "";
                        defaultOption.text = "No hay nada aqui";
                        selectActivos.appendChild(defaultOption);
                
                } else {
        
        
                // Crea una opción por defecto
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "Seleccione";
                selectActivos.appendChild(defaultOption);
                
                // Itera sobre la data para agregar los EQUIPOS al select
                data.data.forEach((item) => {
                
                        const option = document.createElement("option");
        
                        
                
                        option.value = item.id;
                        option.text = item.tag ;
                        selectActivos.appendChild(option);

                        
                });
                }
                } catch (error) {
                console.log("Error en la petición", error);
                }

}
document.getElementById('form-proyect').addEventListener('submit', function(e) {
        e.preventDefault();
        
        Swal.fire({
                title: 'Enviando...',
                text: 'Por favor espere mientras se procesa el formulario',
                icon: 'info',
                allowOutsideClick: false,
                showConfirmButton: false,
                willOpen: () => {
                Swal.showLoading();
                }
        });
        
        // Envía el formulario
        this.submit();
        });

