Highcharts.theme = {
  colors: ["#666666", "#439bfe", "#639632", "#ef6700", "#DDDF0D", "#7798BF", "#55BF3B", "#DF5353", "#aaeeee", "#ff0066", "#eeaaee", "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
  chart: {
    backgroundColor: {
      linearGradient: [0, 0, 0, 400],
      stops: [
        [0, 'rgb(39, 40, 34)'],
        [1, 'rgb(39, 40, 34)']
      ]
    },
    borderWidth: 0,
    borderRadius: 6,
    marginRight: 20,
    marginTop: 45,
    marginBottom: 60,
    plotBackgroundColor: null,
    plotShadow: false,
    plotBorderWidth: 0
  },
  title: {
    style: {
      color: '#76715e',
      font: '500 21px Helvetica Neue, Helvetica, Arial, sans-serif'
    }
  },
  subtitle: {
    style: {
      color: '#DDD',
      font: '12px Helvetica Neue, Helvetica, Arial, sans-serif'
    }
  },
  xAxis: {
    gridLineWidth: 0,
    lineColor: '#76715e',
    tickColor: '#76715e',
    labels: {
      style: {
        color: '#76715e',
        fontWeight: 'bold'
      }
    },
    title: {
      style: {
        color: '#76715e',
        font: 'bold 11px Helvetica Neue, Helvetica, Arial, sans-serif'
      }
    }
  },
  yAxis: {
    alternateGridColor: null,
    minorTickInterval: null,
    gridLineColor: 'rgba(60, 60, 47,)',
    lineWidth: 0,
    tickWidth: 0,
    labels: {
      style: {
        color: '#76715e',
        fontWeight: 'bold'
      }
    },
    title: {
      style: {
        color: '#76715e',
        font: '11px Helvetica Neue, Helvetica, Arial, sans-serif'
      }
    }
  },
  legend: {
    align: 'right',
    verticalAlign: 'top',
    x: -15,
    y: 30,
    floating: true,
    layout: 'vertical',
    borderWidth: 0,
    borderColor: '#fff',
    itemStyle: {
      color: '#76715e'
    },
    itemHoverStyle: {
      color: '#FFF'
    },
    itemHiddenStyle: {
      color: '#333'
    }
  },
  labels: {
    style: {
      color: '#CCC'
    }
  },
  tooltip: {
    backgroundColor: {
      linearGradient: [0, 0, 0, 50],
      stops: [
        [0, 'rgba(96, 96, 96, .8)'],
        [1, 'rgba(16, 16, 16, .8)']
      ]
    },
    borderWidth: 0,
    style: {
      color: '#FFF'
    }
  },

  plotOptions: {
    line: {
      dataLabels: {
        color: '#CCC'
      },
      marker: {
        lineColor: '#333'
      }
    },
    spline: {
      marker: {
        lineColor: '#333'
      }
    },
    scatter: {
      marker: {
        lineColor: '#333'
      }
    },
    candlestick: {
      lineColor: 'white'
    }
  },

  toolbar: {
    itemStyle: {
      color: '#CCC'
    }
  },

  navigation: {
    buttonOptions: {
      backgroundColor: {
        linearGradient: [0, 0, 0, 20],
        stops: [
          [0.4, '#606060'],
          [0.6, '#333333']
        ]
      },
      borderColor: '#000000',
      symbolStroke: '#C0C0C0',
      hoverSymbolStroke: '#FFFFFF'
    }
  },

  exporting: {
    buttons: {
      exportButton: {
        symbolFill: '#55BE3B'
      },
      printButton: {
        symbolFill: '#7797BE'
      }
    }
  },

  // scroll charts
  rangeSelector: {
    buttonTheme: {
      fill: {
        linearGradient: [0, 0, 0, 20],
        stops: [
          [0.4, '#888'],
          [0.6, '#555']
        ]
      },
      stroke: '#000000',
      style: {
        color: '#CCC',
        fontWeight: 'bold'
      },
      states: {
        hover: {
          fill: {
            linearGradient: [0, 0, 0, 20],
            stops: [
              [0.4, '#BBB'],
              [0.6, '#888']
            ]
          },
          stroke: '#000000',
          style: {
            color: 'white'
          }
        },
        select: {
          fill: {
            linearGradient: [0, 0, 0, 20],
            stops: [
              [0.1, '#000'],
              [0.3, '#333']
            ]
          },
          stroke: '#000000',
          style: {
            color: 'yellow'
          }
        }
      }
    },
    inputStyle: {
      backgroundColor: '#333',
      color: 'silver'
    },
    labelStyle: {
      color: 'silver'
    }
  },

  navigator: {
    handles: {
      backgroundColor: '#666',
      borderColor: '#AAA'
    },
    outlineColor: '#CCC',
    maskFill: 'rgba(16, 16, 16, 0.5)',
    series: {
      color: '#7798BF',
      lineColor: '#A6C7ED'
    }
  },

  scrollbar: {
    barBackgroundColor: {
      linearGradient: [0, 0, 0, 20],
      stops: [
        [0.4, '#888'],
        [0.6, '#555']
      ]
    },
    barBorderColor: '#CCC',
    buttonArrowColor: '#CCC',
    buttonBackgroundColor: {
      linearGradient: [0, 0, 0, 20],
      stops: [
        [0.4, '#888'],
        [0.6, '#555']
      ]
    },
    buttonBorderColor: '#CCC',
    rifleColor: '#FFF',
    trackBackgroundColor: {
      linearGradient: [0, 0, 0, 10],
      stops: [
        [0, '#000'],
        [1, '#333']
      ]
    },
    trackBorderColor: '#666'
  },

  // special colors for some of the demo examples
  legendBackgroundColor: 'rgba(48, 48, 48, 0.8)',
  legendBackgroundColorSolid: 'rgb(70, 70, 70)',
  dataLabelsColor: '#444',
  textColor: '#E0E0E0',
  maskColor: 'rgba(255,255,255,0.3)'
};

// Apply the theme
var highchartsOptions = Highcharts.setOptions(Highcharts.theme);