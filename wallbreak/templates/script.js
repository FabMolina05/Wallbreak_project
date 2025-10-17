const btn = document.getElementById("micBtn");
const texto = document.getElementById("texto");
const traduccion = document.getElementById("traduccion");

btn.addEventListener("click", () => {
  btn.classList.toggle("active");

  if (btn.classList.contains("active")) {
    texto.textContent = "🎙️ Escuchando...";
    traduccion.textContent = "⏳ Procesando...";
  } else {
    texto.textContent = "Hola, ¿cómo estás?";
    traduccion.textContent = "Hey, how are you?";
  }
});
