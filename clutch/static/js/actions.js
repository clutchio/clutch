$(function() {

var PRE_ACTIONS = {
    'device-delete': function(elt) {
        return confirm('Are you sure you want to delete this device?');
    },
    'member-remove': function(elt) {
        return confirm('Are you sure you want to remove this member\'s access?');
    },
    'version-bundle-save': function(elt) {
        var form = $(elt).closest('form');
        return {
            'min_bundle': $('.min-bundle', form).val(),
            'max_bundle': $('.max-bundle', form).val()
        };
    },
    'quickstart-add-device': function(elt) {
        var val = $.trim($('#device-udid').val());
        if(!val.length) {
            return alert('You must enter a valid ID value.');
        }
        return {'device_udid': val};
    },
    'quickstart-add-device-2': function(elt) {
        var val = $.trim($('#device-udid-2').val());
        if(!val.length) {
            return alert('You must enter a valid ID value.');
        }
        return {'device_udid': val};
    }
};

var POST_ACTIONS = {
    /*
    'device-make-primary': function(elt, resp) {
    },
    'device-delete': function(elt, resp) {
    },
    'key-deactivate': function(elt, resp) {
    },
    'key-reactivate': function(elt, resp) {
    },
    'key-generate': function(elt, resp) {
    },
    'member-remove': function(elt, resp) {
    },
    */
    'version-bundle-save': function(elt, resp) {
        if(!resp.success){
            return alert('Sorry, there was an error performing your request.');
        }
        if(!resp.success.version) {
            return alert('Sorry, there was an error performing your request.');
        }
        $(elt).closest('form').toggle();
    },
    'quickstart-add-device': function(elt, resp) {
        if(!resp.success){
            return alert('Sorry, there was an error performing your request.');
        }
        $('#device-added-success').show();
        $('#device-udid').val('');
    },
    'quickstart-add-device-2': function(elt, resp) {
        if(!resp.success){
            return alert('Sorry, there was an error performing your request.');
        }
        $('#device-added-success-2').show();
        $('#device-udid-2').val('');
    },
    'DEFAULT': function(elt, resp) {
        document.location.reload(); // Basically don't do AJAX
    }
};

function getDataAttributes(node) {
    var d = {},
        re_dataAttr = /^data\-(.+)$/;

    $.each(node.get(0).attributes, function(index, attr) {
        if (re_dataAttr.test(attr.nodeName)) {
            var key = attr.nodeName.match(re_dataAttr)[1];
            d[key] = attr.nodeValue;
        }
    });

    return d;
}

$('a.action').click(function() {
    var elt = $(this);
    var action = elt.data('action');
    if(!action) {
        return false;
    }
    var data = getDataAttributes(elt);
    var func = PRE_ACTIONS[action];
    if(func) {
        var preResp = func(elt);
        if(!preResp) {
            return false;
        }
        data = $.extend({}, data, preResp);
    }
    var url = '/action/' + action + '.json';
    delete data.action;
    $.getJSON(url, data, function(resp) {
        (POST_ACTIONS[action] || POST_ACTIONS.DEFAULT)(elt, resp);
    });
    return false;
});
 
});