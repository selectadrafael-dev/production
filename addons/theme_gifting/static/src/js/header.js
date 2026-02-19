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

  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target) && e.target !== btn) {
      menu.style.display = "none";
    }
  });

});


//language translator dropdown
document.addEventListener("DOMContentLoaded", function () {

  const btn = document.getElementById("langBtn");
  const menu = document.getElementById("langMenu");

  if (!btn || !menu) return;

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    menu.style.display =
      menu.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target) && e.target !== btn) {
      menu.style.display = "none";
    }
  });

});
