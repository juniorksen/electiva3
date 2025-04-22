// Funciones de las tarjetas
function crearFianza() {
    alert("Función para crear una nueva fianza");
  }
  
  function verListado() {
    alert("Mostrando el listado de fianzas");
  }
  
  function generarReporte() {
    alert("Generando reporte...");
  }
  
  function verHistorial() {
    alert("Mostrando historial de fianzas");
  }
  
  function verEstadisticas() {
    alert("Mostrando estadísticas de fianzas");
  }
  
  function configuracionAvanzada() {
    alert("Accediendo a la configuración avanzada");
  }
  
  function reorderBoxes() {
    const grid = document.querySelector('.grid');
    grid.classList.add('fade-out');
    setTimeout(() => {
      const cards = Array.from(grid.children);
      for (let i = cards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [cards[i], cards[j]] = [cards[j], cards[i]];
      }
      cards.forEach(card => grid.appendChild(card));
      grid.classList.remove('fade-out');
    }, 300);
  }
  
  // Funciones del chat
  function openChat() {
    document.getElementById('chat-panel').classList.remove('hidden');
  }
  
  function closeChat() {
    document.getElementById('chat-panel').classList.add('hidden');
  }
  
  function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message !== "") {
      const chatBody = document.querySelector('.chat-body');
      const messageElem = document.createElement('div');
      messageElem.classList.add('chat-message', 'user-message');
      messageElem.textContent = message;
      chatBody.appendChild(messageElem);
      input.value = "";
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  }
  