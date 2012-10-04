(function() {

var appId = null;
var period = null;
var graphs = {};
var mouseoverTimeouts = {};

function setGlobals() {
  if(!appId) {
    appId = $('#data-app-id').text();
  }
  if(!period) {
    period = $('#period').val();
  }
}

function updateQuick() {
  $.getJSON('/stats/quick/' + appId + '/' + period + '.json', function(data) {
    $('#quick-stats .stat-total-users .stat').text(data.total_users);
    $('#quick-stats .stat-actives .stat').text(data.active_users);
    $('#quick-stats .stat-new-users .stat').text(data.new_users);
    $('#quick-stats .stat-views .stat').text(data.views);
  });
}

function graph(data, klass) {
  var prevData = [];
  for(var i = 0; i < data.stats_prev.length; ++i) {
    prevData[i] = [
      parseInt(data.stats_prev[i].timestamp * 1000.0, 10),
      data.stats_prev[i].stat
    ];
  }
  var currData = [];
  for(var j = 0; j < data.stats.length; ++j) {
    currData[j] = [
      parseInt(data.stats[j].timestamp * 1000.0, 10),
      data.stats[j].stat
    ];
  }

  var series = null;

  var atm = period === 'alltime';
  if(atm) {
    series = [{name: 'All-Time', data: currData, color: '#439bfe'}];
  } else if(period === 'months') {
    series = [
      {
        xAxis: 0,
        name: 'Last 3 Months',
        data: prevData
      },
      {
        xAxis: 1,
        name: 'This 3 Months',
        data: currData
      }
    ];
  } else if(period === 'month') {
    series = [
      {
        xAxis: 0,
        name: 'Last Month',
        data: prevData
      },
      {
        xAxis: 1,
        name: 'This Month',
        data: currData
      }
    ];
  } else if(period === 'today') {
    series = [
      {
        xAxis: 0,
        name: 'Yesterday',
        data: prevData
      },
      {
        xAxis: 1,
        name: 'Today',
        data: currData
      }
    ];
  }

  var title = null;
  var height = null;
  var width = null;
  if(klass === 'stat-actives-graph') {
    title = {text: 'Active Users'};
    height = '300';
    width = '692';
  } else if(klass === 'stat-new-users-graph') {
    title = {text: 'New Users'};
    height = '200';
    width = '692';
  } else if(klass === 'stat-views-graph') {
    title = {text: 'Views'};
    height = '200';
    width = '692';
  } else if(klass === 'stat-total-users-graph') {
    title = {text: 'Total Users'};
    height = '200';
    width = '692';
  }

  var opts = {
    chart: {
      renderTo: klass,
      height: height,
      width: width,
      type: 'line'
    },
    title: title,
    xAxis: atm ? {type: 'datetime'} : [
      {type: 'datetime', labels: {enabled: false}},
      {type: 'datetime'}
    ],
    yAxis: {
      type: 'linear',
      min: 0,
      title: null
    },
    series: series
  };

  var chart = new Highcharts.Chart(opts);
}

function updateActives() {
  $.getJSON('/stats/actives/' + appId + '/' + period + '.json', function(data) {
    graph(data, 'stat-actives-graph');
  });
}

function updateNewUsers() {
  $.getJSON('/stats/new-users/' + appId + '/' + period + '.json', function(data) {
    graph(data, 'stat-new-users-graph');
  });
}

function updateViews() {
  $.getJSON('/stats/views/' + appId + '/' + period + '.json', function(data) {
    graph(data, 'stat-views-graph');
  });
}

function updateTotalUsers() {
  $.getJSON('/stats/total-users/' + appId + '/' + period + '.json', function(data) {
    graph(data, 'stat-total-users-graph');
  });
}

function updateScreenViews() {
  var currentScreen = $('#screen').val();
  if(!currentScreen) {
    return;
  }
  $.getJSON('/stats/screen-views/' + currentScreen + '/' + appId + '/' + period + '.json', function(data) {
    graph(data, 'stat-screen-views-graph');
  });
}

function updateStats() {
  if($('#screen').length) {
    updateScreenViews();
  } else {
    updateQuick();
    updateActives();
    updateNewUsers();
    updateViews();
    updateTotalUsers();
  }
}

function periodChanged() {
  var parts = location.pathname.split('/');
  if(parts.length === 4) {
    parts[3] = 'stats';
  } else if(parts.length === 5) {
    parts.push('');
  }
  parts[4] = $('#period').val();
  location.pathname = parts.join('/');
}

function screenChanged() {
  var parts = location.pathname.split('/');
  parts[5] = $('#screen').val();
  location.pathname = parts.join('/');
}

$(function() {
  setGlobals();
  $('#period').change(periodChanged);
  if($('#screen').length) {
    $('#screen').change(screenChanged);
  }
  updateStats();
  setInterval(updateStats, 30 * 1000);
});

})();