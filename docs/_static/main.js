function setupClientDownloadLink() {
    var elt = $('#command-line-client-download');
    if(!elt.length) {
        return;
    }
    var popup = $('#command-line-client-download-info');
    var timeout = null;
    function hoverIn(e) {
        if(timeout) {
            clearTimeout(timeout);
        }
        popup.slideDown(200);
    }
    function hoverOut(e) {
        if(timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(function() {
            popup.slideUp(200);
        }, 1000);
    }
    popup.hover(hoverIn, hoverOut);
    elt.hover(hoverIn, hoverOut).click(function(e) {
        return false;
    });
}

jQuery.fn.highlight = function(pat, wrapName) {
 function innerHighlight(node, pat) {
  var skip = 0;
  if (node.nodeType == 3) {
   var pos = node.data.toUpperCase().indexOf(pat);
   if (pos >= 0) {
    var spannode = document.createElement('span');
    spannode.className = wrapName;
    var middlebit = node.splitText(pos);
    var endbit = middlebit.splitText(pat.length);
    var middleclone = middlebit.cloneNode(true);
    spannode.appendChild(middleclone);
    middlebit.parentNode.replaceChild(spannode, middlebit);
    skip = 1;
   }
  }
  else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
   for (var i = 0; i < node.childNodes.length; ++i) {
    i += innerHighlight(node.childNodes[i], pat);
   }
  }
  return skip;
 }
 return this.each(function() {
  innerHighlight(this, pat.toUpperCase());
 });
};

function setupAddingNewScreenTutorial() {
    var elt = $('#adding-a-new-screen');
    if(!elt.length) {
        return;
    }
    var slugElt = $('#id_slug');
    var nameElt = $('#id_name');
    elt.highlight('$SLUG$', 'slug-wrap');
    elt.highlight('$NAME$', 'name-wrap');
    function update() {
        $('.slug-wrap').text(slugElt.val());
        $('.name-wrap').text(nameElt.val());
    }
    slugElt.keyup(update).change(update);
    nameElt.keyup(update).change(update);
    update();
}

$(function() {
    setupClientDownloadLink();
    setupAddingNewScreenTutorial();
});