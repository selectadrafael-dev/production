odoo.define('theme_gifting.header', function (require) {
  "use strict";

  document.addEventListener("click", function (e) {

    /* =============================
       CATEGORY DROPDOWN
    ============================= */

    const catBtn = e.target.closest("#catToggle");
    const catMenu = document.getElementById("catDropdown");

    if (catBtn && catMenu) {
      e.stopPropagation();

      catMenu.style.display =
        catMenu.style.display === "block" ? "none" : "block";

      return;
    }

    if (catMenu && !e.target.closest("#catDropdown")) {
      catMenu.style.display = "none";
    }

    /* =============================
       LANGUAGE DROPDOWN
    ============================= */

    const langBtn = e.target.closest("#langBtn");
    const langMenu = document.getElementById("langMenu");

    if (langBtn && langMenu) {
      e.stopPropagation();

      langMenu.style.display =
        langMenu.style.display === "block" ? "none" : "block";

      return;
    }

    if (langMenu && !e.target.closest("#langMenu")) {
      langMenu.style.display = "none";
    }

  });

});
