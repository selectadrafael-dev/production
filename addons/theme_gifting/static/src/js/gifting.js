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

  /*most populous categories */
  // =====================================================
// POPULAR CATEGORY CAROUSEL
// =====================================================
// =====================================================
// POPULAR CATEGORY CAROUSEL
// =====================================================

document.addEventListener(

    'DOMContentLoaded',

    function () {

        const track = document.getElementById(
            'popularCategoryTrack'
        );

        if (!track) {

            return;
        }

        const items = track.querySelectorAll(
            '.popular-category-item'
        );

        const nextBtn = document.getElementById(
            'popularCategoryNext'
        );

        const prevBtn = document.getElementById(
            'popularCategoryPrev'
        );

        let currentIndex = 0;


        function visibleItems() {

            if (window.innerWidth <= 768) {

                return 1;
            }

            if (window.innerWidth <= 1200) {

                return 3;
            }

            return 5;
        }


        function slideTo(

            index,

            speed = '0.55s'

        ) {

            const item = items[0];

            if (!item) {

                return;
            }

            const gap = 20;

            const width =
                item.offsetWidth + gap;

            track.style.transition =
                `transform ${speed} ease`;

            track.style.transform =
                `translateX(-${index * width}px)`;
        }


        function nextSlide() {

            const visible =
                visibleItems();

            const max =
                items.length - visible;

            currentIndex++;

            if (currentIndex > max) {

                slideTo(
                    currentIndex,
                    '0.35s'
                );

                setTimeout(function () {

                    currentIndex = 0;

                    slideTo(
                        0,
                        '0.05s'
                    );

                }, 350);

                return;
            }

            slideTo(currentIndex);
        }


        function prevSlide() {

            currentIndex--;

            if (currentIndex < 0) {

                currentIndex = 0;
            }

            slideTo(currentIndex);
        }


        nextBtn.addEventListener(
            'click',
            nextSlide
        );

        prevBtn.addEventListener(
            'click',
            prevSlide
        );


        setInterval(function () {

            nextSlide();

        }, 3500);

    }
);


})();