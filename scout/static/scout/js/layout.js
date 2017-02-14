var Layout = {

    init_layout: function(){

        // async load css by flipping the media attribute to all
    	$('link[rel="stylesheet"]').attr('media', 'all');

        var isMobile = $("body").data("mobile");

        var offsetHeight;

        // set min height for pages
        if ($('#page_discover').length > 0) {

            // discover page doesn't have filter results display
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-discover-container").css({minHeight: $(window).outerHeight() - offsetHeight });

            // 404 page
            if($("#page_404").length > 0) {
                var offsetHeight = ($(".scout-header").outerHeight() + $(".scout-footer").outerHeight());
                $("#page_404").css({minHeight: $(window).outerHeight() - offsetHeight });
            }

        } else if ($('#page_filter').length > 0)  {

            // filter page doesn't have geolocation bar
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-filter-container").css({minHeight: $(window).outerHeight() - (offsetHeight + 10) });

        } else {

            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-filter-results").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-list-container").css({minHeight: $(window).outerHeight() - offsetHeight });

        }

        // if mobile, calculate height of image container
        if (isMobile !== undefined ) {
            var aspectHeight = Math.round(( $(".spot-detail-main-image").width() /100)*67); //(i.e. 16:9 or 100:67)
            $(".spot-detail-main-image").height(aspectHeight);
            $(".scout-spot-gallery").css('max-height', aspectHeight);
        }
        $(document).on('click', 'form#occupy button.minutes', function (e) {
            e.preventDefault();

            var input = e.target;
            var form = input.form;
            var url = window.location.href + $(form).attr('action');
            var data = $(form).serialize() + '&minutes=' + $(input).val();

            $('div.scout-spot-occupy div.spot-form').hide();
            $('div.scout-spot-occupy div.spot-spinner').show();

            $.ajax({
                type: 'POST',
                url: url,
                data: data,
                success: function(data) {
                    $('div.scout-spot-occupy').replaceWith(data);
                }
            })
        })

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });

        function getCookie(c_name) {
            if (document.cookie.length > 0)
            {
                c_start = document.cookie.indexOf(c_name + "=");
                if (c_start != -1)
                {
                    c_start = c_start + c_name.length + 1;
                    c_end = document.cookie.indexOf(";", c_start);
                    if (c_end == -1) c_end = document.cookie.length;
                    return unescape(document.cookie.substring(c_start,c_end));
                }
            }
            return "";
        }

    },
};
