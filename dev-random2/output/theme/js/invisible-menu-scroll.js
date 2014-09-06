function invisibleMenu() {

    var now = 0;
    var pixels =  300;
    var opacity = 1;

    var move = function() { 
        now = $(window).scrollTop();
        if (now > pixels && opacity !== 0)
            opacity = 0;
        else if(now < pixels){
            //Depends on the position not if scrolls down or up
            opacity = (1 - now/pixels);
        }
        $("div.social-navigation").css({"opacity": opacity});
        if (opacity <= 0) {
          $("div.social-navigation").hide();
        } else {
          $("div.social-navigation").show();
        }    
    };
    $(window).scroll(move);
    move();
}
