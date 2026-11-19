(function () {
  "use strict";

  // Cerrar avisos.
  document.querySelectorAll("[data-toast-close]").forEach(function (button) {
    button.addEventListener("click", function () {
      button.closest(".toast").remove();
    });
  });

  // Reloj del pie de página, en la hora del visitante.
  var clock = document.querySelector("[data-clock]");
  if (clock) {
    var tick = function () {
      clock.textContent = new Date().toLocaleTimeString("es", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      });
    };
    tick();
    setInterval(tick, 10000);
  }

  // Un .mp4 que termina se marca como visto solo. YouTube y Vimeo usan el botón.
  var player = document.querySelector("video[data-autocomplete-form]");
  if (player) {
    player.addEventListener("ended", function () {
      var form = document.getElementById(player.dataset.autocompleteForm);
      if (form) form.submit();
    });
  }

  // Detalle por día en el gráfico de flujo.
  var chart = document.querySelector("[data-flow-chart]");
  if (chart) {
    var tooltip = chart.querySelector(".chart-tooltip");
    var crosshair = chart.querySelector(".crosshair");
    var svg = chart.querySelector("svg");
    var hide = function () {
      tooltip.hidden = true;
      crosshair.style.display = "none";
    };
    var show = function (hit) {
      var d = hit.dataset;
      tooltip.innerHTML = "";
      var title = document.createElement("strong");
      title.textContent = d.day;
      tooltip.appendChild(title);
      [
        ["s-active", "Usuarios activos", d.active],
        ["s-register", "Registros", d.registers],
        ["s-delete", "Eliminaciones", d.deletes],
        ["", "Inicios de sesión", d.logins],
      ].forEach(function (item) {
        var row = document.createElement("span");
        row.className = "chart-tooltip-row";
        var key = document.createElement("i");
        key.className = "key " + item[0];
        var label = document.createElement("span");
        label.textContent = item[1];
        var value = document.createElement("b");
        value.textContent = item[2];
        row.append(key, label, value);
        tooltip.appendChild(row);
      });
      tooltip.hidden = false;
      crosshair.setAttribute("x1", d.x);
      crosshair.setAttribute("x2", d.x);
      crosshair.style.display = "";
      var scale = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
      var left = parseFloat(d.x) * scale;
      var width = tooltip.offsetWidth;
      var fits = left + 14 + width <= chart.clientWidth;
      tooltip.style.left = (fits ? left + 14 : Math.max(left - width - 14, 0)) + "px";
    };
    chart.querySelectorAll(".hit").forEach(function (hit) {
      hit.addEventListener("mouseenter", function () { show(hit); });
      hit.addEventListener("focus", function () { show(hit); });
      hit.addEventListener("blur", hide);
    });
    chart.addEventListener("mouseleave", hide);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") hide();
    });
  }
})();
