var $ = require("jquery");

$(function() {
  var $win = $(window),
      offset = 225;

  $win.on("scroll", function() {
    var currentScroll = $win.scrollTop();
    if (currentScroll > offset) {
      $(".page-nav").addClass("scrolled");
    } else {
      $(".page-nav").removeClass("scrolled");
    }
  });
});
