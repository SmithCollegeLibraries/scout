var pathname, map, marker;
var myLatlng, mapOptions;
            
function initializeMap() {
   
    pathname = window.location.pathname;
    
    $('.overlay').remove();
    
    // url routing 
        
    if (pathname.indexOf("/seattle/food/18374") >= 0) {
            
        // uw fountain
        myLatlng = new google.maps.LatLng(47.653811, -122.307815);
        mapOptions = { center: myLatlng, zoom: 18, scrollwheel: false, draggable: false, disableDefaultUI: true };
        
    }
    else if (pathname.indexOf("/favorites/56874") >= 0) {
            
        // uw fountain
        myLatlng = new google.maps.LatLng(47.653811, -122.307815);
        mapOptions = { center: myLatlng, zoom: 17, scrollwheel: false, draggable: false, disableDefaultUI: true };
        
    }
    else if (pathname.indexOf("/seattle/food/") >= 0) {
            
        // uw fountain
        myLatlng = new google.maps.LatLng(47.653811, -122.307815);
        mapOptions = { center: myLatlng, zoom: 17, scrollwheel: false};
                    
    }
    else {
         
        // seattle
        myLatlng = new google.maps.LatLng(47.653811, -122.307815);
        mapOptions = { center: myLatlng, zoom: 16 };
        
        $('#map').append('<div class="overlay"></div>');
    }
    

    // load the map only if map-canvas exists
        
    if (document.getElementById("map-canvas")) {
        
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
                    
    marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            title: 'Hello World!',
            animation: google.maps.Animation.DROP,
        });
                
    }
    
}
