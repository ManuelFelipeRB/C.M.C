// Elimina la función que hace fetch porque ya no es necesario hacer una solicitud a la API
async function cargarPesajes() {
    try {
        // Este código ya no es necesario
        const response = await fetch("http://localhost:5001/api/pesajes");
        const data = await response.json();

        let tabla = document.querySelector(".recentOrders tbody");
        tabla.innerHTML = "";  // Limpia la tabla antes de insertar nuevos datos

        data.forEach(pesaje => {
            let fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${pesaje.Nombre || 'N/A'}</td>
                <td>${pesaje.Placa || 'N/A'}</td>
                <td>${pesaje.Producto || 'N/A'}</td>
                <td><span class="status delivered">${pesaje.Status || 'N/A'}</span></td>
            `;
            tabla.appendChild(fila);
        });

    } catch (error) {
        console.error("Error cargando datos:", error);
    }
}

// Ejecuta la función cuando cargue la página
window.onload = cargarPesajes;
fetch('/api/pesajes')
  .then(response => response.json())
  .then(data => {
      // Procesa los datos aquí
      console.log(data);
  })
  .catch(error => {
      console.error('Error cargando datos:', error);
  });
