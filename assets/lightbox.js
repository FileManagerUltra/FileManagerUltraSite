(function () {
  var imgs = document.querySelectorAll("figure picture img");
  if (!imgs.length || typeof HTMLDialogElement === "undefined") return;

  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.setAttribute("aria-label", "Screenshot, enlarged");
  var big = document.createElement("img");
  var close = document.createElement("button");
  close.type = "button";
  close.className = "lightbox-close";
  close.setAttribute("aria-label", "Close");
  close.textContent = "\u00d7";
  dlg.appendChild(big);
  dlg.appendChild(close);
  document.body.appendChild(dlg);

  function open(img) {
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    dlg.showModal();
  }
  dlg.addEventListener("click", function () { dlg.close(); });

  imgs.forEach(function (img) {
    img.classList.add("zoomable");
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.title = "Click to enlarge";
    img.addEventListener("click", function () { open(img); });
    img.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(img); }
    });
  });
})();
