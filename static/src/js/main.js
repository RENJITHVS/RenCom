$(document).ready(function () {

  // Sticky Menu
  $(window).on('scroll', function () {
    var scroll = $(window).scrollTop();
    if (scroll < 5) {
      $(".header-bottom").removeClass("sticky");
    } else {
      $(".header-bottom").addClass("sticky");
    }
  });

  //Brand_slider
  $('.brand-area').slick({
    infinite: true,
    slidesToShow: 5,
    slidesToScroll: 1,
    arrows: false,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1,
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1
        }
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
  });

  //testimonial_slider
  $('.features-active').slick({
    infinite: true,
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: true,
    arrows: true,
    autoplaySpeed: 2000,
    prevArrow: '.features-wrapper .prev-arrow',
    nextArrow: '.features-wrapper .next-arrow',
    responsive: [{
        breakpoint: 1025,
        settings: {
          slidesToShow: 3,
          dots: true,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          dots: true,
        },
      },
    ],
  });

  //Customersreview Slider
  $('.customersreview-active').slick({
    infinite: true,
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: false,
    arrows: true,
    autoplaySpeed: 2000,
    prevArrow: '.customersreview-wrapper .prev-arrow',
    nextArrow: '.customersreview-wrapper .next-arrow',
    responsive: [{
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          dots: true,
        },
      },
      {
        breakpoint: 481,
        settings: {
          slidesToShow: 1,
          dots: true,
        },
      },
    ],
  });


  //Product Details Slider
  $("#exzoom").exzoom({
    // thumbnail nav options
    "navWidth": 60,
    "navHeight": 60,
    "navItemNum": 5,
    "navItemMargin": 7,
    "navBorder": 0,
    // autoplay
    "autoPlay": false,
    // autoplay interval in milliseconds
    "autoPlayTimeout": 2000

  });

  //Active size
  $('#sizes li').on('click', function () {
    $(this).addClass('active').siblings().removeClass('active');
  });


  //Active color
  $('#colors li').on('click', function () {
    $(this).addClass('active').siblings().removeClass('active');
  });


});

//nice-select
$(document).ready(function () {
  $('select').niceSelect();
});
