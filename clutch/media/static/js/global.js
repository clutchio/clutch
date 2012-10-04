$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

$.support.transition = (function () {
  var thisBody = document.body || document.documentElement,
    thisStyle = thisBody.style,
    support = thisStyle.transition !== undefined || thisStyle.WebkitTransition !== undefined || thisStyle.MozTransition !== undefined || thisStyle.MsTransition !== undefined || thisStyle.OTransition !== undefined;

  return support && {
    end: (function () {
      var transitionEnd = "TransitionEnd";
      if ( $.browser.webkit ) {
        transitionEnd = "webkitTransitionEnd";
      } else if ( $.browser.mozilla ) {
        transitionEnd = "transitionend";
      } else if ( $.browser.opera ) {
        transitionEnd = "oTransitionEnd";
      }
      return transitionEnd;
    }())
  };
})();

$(function() {
    $('.alert-message a.close').live('click', function(e) {
        var elt = $(this).closest('.alert-message');
        elt.fadeOut(function() {
            elt.remove();
        });
        return false;
    });
    $('.show-toggle').click(function() {
        $('.bundles', $(this).parent()).toggle();
    });
    $('#app-jumper').change(function() {
        document.location = this.options[this.selectedIndex].value;
        return false;
    });

    ///////////////////////

    $("ul.dropdown li").hover(function(){
        $(this).addClass("hover");
        $('ul:first',this).css('display', 'block');
    }, function(){
        $(this).removeClass("hover");
        $('ul:first',this).css('display', 'none');
    });

    ///////////////////////

    if($.fn.tooltip !== undefined) {
        $("[rel=tooltip]").tooltip();
    }
    if($.fn.popover !== undefined) {
        $('a[rel="popover"]').popover();
    }
});

