//product category
document.addEventListener("DOMContentLoaded", function () {

  const btn = document.getElementById("catToggle");
  const menu = document.getElementById("catDropdown");

  if (!btn || !menu) return;

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    menu.style.display =
      menu.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", function () {
    menu.style.display = "none";
  });

});

//language translator dropdown
const langBtn = document.getElementById("langBtn");
const langMenu = document.getElementById("langMenu");

if (langBtn && langMenu) {

  langBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    langMenu.style.display =
      langMenu.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", function () {
    langMenu.style.display = "none";
  });

}

