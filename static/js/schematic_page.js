function updateStatus() {
  fetch("/dynamic_update")
    .then(res => res.json())
    .then(data => {
      data.lamps.forEach(lamp => {
        document.getElementById(lamp.id).style.backgroundColor = lamp.color;
      });
      data.texts.forEach(txt => {
        document.getElementById(txt.id).textContent = txt.value;
      });
    });
}

// elke 2 seconden status ophalen
setInterval(updateStatus, 2000);
updateStatus();
