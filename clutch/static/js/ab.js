function roundFloat(original) {
  return Math.round(original * 100) / 100;
}

function showGraph(data) {

  var series = [];
  var i = -1;
  while(true) {
    var graphData = data.graphs[i];
    if(!graphData) {
      break;
    }
    var tmp = [];
    for(var j = 0; j < graphData.length; ++j) {
      var itemData = graphData[j];
      if(!itemData.timestamp) {
        continue;
      }
      var val;
      if(itemData.trials === 0) {
        val = 0;
      } else {
        val = roundFloat(itemData.successes * 100.0 / itemData.trials);
      }
      tmp[j] = [parseInt(itemData.timestamp * 1000.0, 10), val];
    }
    if(i == -1) {
      series[i + 1] = {
        name: 'Baseline',
        data: tmp
      };
    } else {
      series[i + 1] = {
        name: window.variations[i + 1],
        data: tmp
      };
    }
    ++i;
  }

  var opts = {
    chart: {
      renderTo: 'chart',
      height: '350',
      type: 'line'
    },
    title: {
      text: 'Conversion Rates Over Time'
    },
    xAxis: {
      type: 'datetime'
    },
    yAxis: {
      type: 'linear',
      min: 0,
      max: 100,
      title: {
        text: 'Conversion Rate Percentage'
      },
      labels: {
        formatter: function() {
          return this.value + '%';
        }
      }
    },
    series:series
  };

  var chart = new Highcharts.Chart(opts);
}

function showConfidence(data) {
  var i = 0;
  var a = new Abba.Abba('Baseline', data.confidence[-1][0], data.confidence[-1][1]);
  while(true) {
    var item = data.confidence[i];
    if(!item) {
      break;
    }
    var successes = item[0];
    var trials = item[1];
    a.addVariation(window.variations[i + 1], successes, trials);
    ++i;
  }
  if(a) {
    a.renderTo('#confidence');
  }
}

function showGraphAndConfidence() {
  $.getJSON(window.abStatUrl, function(data) {
    var i = -1;
    var count = 0;
    while(true) {
      var item = data.confidence[i];
      if(!item) {
        break;
      }
      count += item[1];
      ++i;
    }
    if(count === 0) {
      $('#chart-heading').hide();
      $('#confidence-heading').hide();
      $('#no-data-yet').show();
      $('.chart-holder').addClass('no-data');
      return;
    }
    showGraph(data);
    showConfidence(data);
  });
}

function getVariationId(container) {
  return parseInt(container.attr('id').replace('variation-', ''), 10);
}

var SLIDERS = [];
function setupSlider(i, elt, currentVals) {
  var container = elt.closest('li');
  var variationId = getVariationId(container);
  var dataSpan = $('.slider-data', container);
  currentVals[i] = parseFloat(dataSpan.text());
  var updateFunc = function(ev, ui) {
    currentVals[i] = ui.value;
    
    var maxVal = 0.0;
    for(var j = 0; j < currentVals.length; ++j) {
      maxVal += currentVals[j];
    }
    dataSpan.text(roundFloat(ui.value));
    $('.total-percentage').html(roundFloat(maxVal) + '%');
    if(maxVal > 100) {
      $('.status').removeClass('warning');
      $('.status').addClass('failure');
    } else if(maxVal > 90) {
      $('.status').addClass('warning');
      $('.status').removeClass('failure');
    } else {
      $('.status').removeClass('warning');
      $('.status').removeClass('failure');
    }
    
    var baseline = 100 - maxVal;
    if(baseline < 0) {
      baseline = 0;
    }
    $('#variation-baseline .slider').slider({value: baseline});
    $('#variation-baseline .slider-data').text(baseline);
  };
  SLIDERS[i] = elt.slider({
    value: currentVals[i],
    step: 1,
    change: updateFunc,
    slide: updateFunc
  });
}

function setupBaseSlider(elt, currentVals) {
  var container = elt.closest('li');
  var dataSpan = $('.slider-data', container);
  elt.slider({
    value: parseFloat(dataSpan.text()),
    step: 1,
    disabled: true
  });
}

function setupSliders() {
  var currentVals = [];
  $('.slider').each(function(i) {
    if(i === 0) {
      setupBaseSlider($(this), currentVals);
      return;
    }
    setupSlider(i - 1, $(this), currentVals);
  });
}

function variationNameEditClicked(ev) {
  var container = $(this).closest('li');
  $('.variation-name', container).hide();
  $('.variation-name-text', container).show();
  $('.variation-name-edit', container).hide();
  $('.variation-name-save', container).show();
  return false;
}

function variationNameSaveClicked(ev) {
  var container = $(this).closest('li');
  var variationId = getVariationId(container);

  var v = $('.variation-name-text', container).hide().val();
  $('.variation-name', container).text(v).show();
  $('.variation-name-edit', container).show();
  $('.variation-name-save', container).hide();

  var url = '/app/' + window.appSlug + '/variation/' + variationId + '/change-name/';
  $.post(url, {name: v}, 'json');

  return false;
}

function setupVariationNameEditor() {
  $('.variation-name-edit').on('click', variationNameEditClicked);
  $('.variation-name-save').on('click', variationNameSaveClicked);
}

function variationRemoveClicked(ev) {
  if(!confirm('Are you sure you want to remove this variation?')) {
    return false;
  }
  var container = $(this).closest('li');
  var variationId = getVariationId(container);
  container.remove();

  var url = '/app/' + window.appSlug + '/variation/' + variationId + '/remove/';
  $.post(url, 'json');

  return false;
}

function setupRemoveVariationButtons() {
  $('.variation-remove').on('click', variationRemoveClicked);
}

function addVariationClicked(ev) {
  // TODO: Make this not be a full-page refresh

  var url = '/app/' + window.appSlug + '/experiment/' + window.experimentId + '/create-variation/';
  $.post(url, function(data) {
    location.reload();
  }, 'json');

  return false;
}

function setupAddVariation() {
  $('.add-variation').on('click', addVariationClicked);
}

var EDITORS = [];
function setupEditors() {
  var JSONMode = require('ace/mode/json').Mode;
  $('.variation-data').each(function(i) {
    var elt = $(this);
    if(elt.text().length) {
      try {
        elt.text(JSON.stringify(JSON.parse(elt.text()), null, 4));
      } catch(e) {}
    } else {
      elt.text('{\n}');
    }
    var container = elt.closest('li');
    var variationId = getVariationId(container);
    var editor = ace.edit('variation-data-' + variationId);
    editor.setTheme('ace/theme/tomorrow');
    editor.getSession().setMode(new JSONMode());
    editor.setHighlightActiveLine(false);
    //editor.renderer.setShowGutter(false);
    EDITORS[i] = editor;
  });
}

function mainFormSubmitted(ev) {
  if($('.status').hasClass('failure')) {
    alert('Sorry, your test variation percentages can add up to a maximum of 100%.');
    return false;
  }

  var data = [];

  var variations = $('.variation');
  for(var i = 0; i < variations.length; ++i) {
    var container = $(variations[i]);

    if(container.attr('id') === 'variation-baseline') {
      continue;
    }

    var variationId = getVariationId(container);

    var slider = SLIDERS[i - 1];
    var sliderVal = slider.slider('value');
    var editor = EDITORS[i - 1];
    var editorVal = '';
    if(editor) {
      editorVal = editor.getSession().getValue();
      try {
        editorVal = JSON.stringify(JSON.parse(editorVal), null, 4);
        $('#variation-data-' + variationId).css('border', 'none');
      } catch(e) {
        $('#variation-data-' + variationId).css('border', '2px solid red');
        alert('Sorry, you entered invalid JSON for "' + window.variations[i] + '"');
        return false;
      }
    }

    data[i - 1] = {id: variationId, weight: sliderVal / 100.0, data: editorVal};
  }

  var url = '/app/' + window.appSlug + '/experiment/' + experimentId + '/save-data/';
  $.post(url, JSON.stringify(data), function(resp) {
    $('#save-data-success').show();
    setTimeout(function() {
      $('#save-data-success').fadeOut();
    }, 5000);
  }, 'json');

  return false;
}

function setupMainForm() {
  $('#main-form').on('submit', mainFormSubmitted);
}

function deleteExperimentClicked(ev) {
  if(!confirm('Are you sure you want to delete this experiment?')) {
    return false;
  }
  var url = '/app/' + window.appSlug + '/experiment/' + experimentId + '/delete/';
  $.post(url, function(resp) {
    window.location = '/app/' + window.appSlug + '/experiments/';
  }, 'json');
  return false;
}

function setupDeleteExperiment() {
  $('.delete-exp').on('click', deleteExperimentClicked);
}

$(function() {
  showGraphAndConfidence();
  setupSliders();
  setupVariationNameEditor();
  setupRemoveVariationButtons();
  setupAddVariation();
  setupEditors();
  setupMainForm();
  setupDeleteExperiment();
});