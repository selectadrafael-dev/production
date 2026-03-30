(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // Example hover animation enhancement
    const cards = document.querySelectorAll('.product-card');

    cards.forEach(function(card){
      card.addEventListener('mouseenter', function(){
        card.classList.add('hovered');
      });
      card.addEventListener('mouseleave', function(){
        card.classList.remove('hovered');
      });
    });

  });
})();