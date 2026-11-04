(function () {
  var root = document.documentElement;
  var KEY = "fmu-theme";
  var buttons = document.querySelectorAll(".theme-toggle button");
  var sources = document.querySelectorAll('picture source[media*="prefers-color-scheme"]');
  sources.forEach(function (s) { s.dataset.media = s.getAttribute("media"); });

  function apply(mode) {
    if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
    sources.forEach(function (s) {
      var wantsDark = s.dataset.media.indexOf("dark") !== -1;
      if (mode === "dark") s.setAttribute("media", wantsDark ? "all" : "not all");
      else if (mode === "light") s.setAttribute("media", wantsDark ? "not all" : "all");
      else s.setAttribute("media", s.dataset.media);
    });
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.mode === mode)); });
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  apply(saved === "light" || saved === "dark" ? saved : "auto");
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      apply(b.dataset.mode);
      try { b.dataset.mode === "auto" ? localStorage.removeItem(KEY) : localStorage.setItem(KEY, b.dataset.mode); } catch (e) {}
    });
  });
})();
