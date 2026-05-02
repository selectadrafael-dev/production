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

// =====================================================
// POPULAR CATEGORY CAROUSEL
// =====================================================

document.addEventListener(

    'DOMContentLoaded',

    function () {

        const carousel =
            document.getElementById(
                'popularCategoryCarousel'
            );

        if (!carousel) {

            return;
        }


        carousel.addEventListener(

            'slid.bs.carousel',

            function () {

                const active =
                    carousel.querySelector(
                        '.carousel-item.active'
                    );

                const items =
                    carousel.querySelectorAll(
                        '.carousel-item'
                    );


                const last =
                    items[
                        items.length - 1
                    ];


                if (active === last) {

                    setTimeout(function () {

                        bootstrap.Carousel
                            .getInstance(
                                carousel
                            )
                            .to(0);

                    }, 250);
                }
            }
        );

    }
);

})();