$(document).on('ready', function(event) {

    Layout.init_layout();
    Navigation.set_page_tab();

    // page based JS calls
    var page_path = window.location.pathname;

    if (page_path.indexOf("food") !== -1) {
        // food
        List.init();
        Map.init_map();
        Filter.init();
        console.log("on food");
    }
    else if (page_path.indexOf("study") !== -1){
        console.log("on study");
    }
    else if (page_path.indexOf("tech") !== -1){
        console.log("on tech");
    }
    else if (page_path.indexOf("map") !== -1){
        // mobile map
        //Map.init_map_page();
        //List.init();
        //Map.init_map();
    }
    else {
        Discover.init_cards();
    }

    Filter.replace_food_href();

    // call this last so all page level location event listeners have been declared
    Geolocation.update_location();

    Filter.init_events();

});

$(window).scroll(function(){

    var isMobile = $("body").data("mobile");

    if (isMobile) {
        var sticky = $('.sticky'),
            scroll = $(window).scrollTop();

        if (scroll >= 200) sticky.addClass('fixed');
        else sticky.removeClass('fixed');
    }

});
