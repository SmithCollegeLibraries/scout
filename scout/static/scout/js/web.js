$(document).on('ready', function(event) {

    Layout.init_layout();
    Navigation.set_campus_selection();

    // page based JS calls
    var page_path = window.location.pathname;

    if (page_path.indexOf("food") !== -1) {
        // food
        Geolocation.display_location_status();
        List.init();
        Map.init_map();
        Filter.init();
    } else if (page_path.indexOf("study") !== -1){
        Geolocation.display_location_status();
        List.init();
        Map.init_map();
        Filter.init();

        // initialize slick image slider
        $('.scout-spot-gallery').slick({
            dots: true,
            arrows: false,
        });

    } else if (page_path.indexOf("tech") !== -1) {
        Geolocation.display_location_status();
        List.init();
        Map.init_map();
        Filter.init();

    } else {
        Discover.init_cards();
        Map.init_map();
    }

    // freeze body for mobile maps
    if (page_path.indexOf("map") !== -1) {
        $("body").addClass("freeze");
        Layout.init_mobile_map();
    } else {
        $("body").removeClass("freeze");
    }


    Filter.replace_navigation_href();
    // call this last so all page level location event listeners have been declared
    Geolocation.update_location();
    Filter.init_events();

});

$(window).scroll(function(){
    var isMobile = $("body").data("mobile");
});
