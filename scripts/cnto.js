var $ = require("jquery");

$(function() {
  var $win = $(window),
      $pages = $(".cnto-page");

  $win.on("scroll", function() {
    var scrollTop = $win.scrollTop();

    $pages.each(function(idx, page) {
      var $page = $(page),
          pageTop = $page.offset().top,
          top = pageTop - scrollTop;

      if (top < 10) {
        $page.find(".page-nav").addClass("scrolled");
      } else {
        $page.find(".page-nav").removeClass("scrolled");
      }
    });
  });
});
