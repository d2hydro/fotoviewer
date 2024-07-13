var projectionExtent = [-285401.92, 22598.08, 595401.9199999999, 903401.9199999999];
var projection = new ol.proj.Projection({
  code: 'EPSG:28992',
  units: 'm',
  extent: projectionExtent
});

// Background layers
var brtWaterLayer = new ol.layer.Tile({
  source: new ol.source.XYZ({
    url: 'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/water/EPSG:28992/{z}/{x}/{y}.png',
    format: 'image/png',
    projection: projection,
    matrixSet: 'EPSG:28992',
    style: 'default',
    tileGrid: new ol.tilegrid.WMTS({
      origin: ol.extent.getTopLeft(projectionExtent),
      resolutions: [
        3440.640,
        1720.320,
        860.160,
        430.080,
        215.040,
        107.520,
        53.760,
        26.880,
        13.440,
        6.720,
        3.360,
        1.680,
        0.840,
        0.420,
        0.210
      ],
      matrixIds: ['EPSG:28992:0', 'EPSG:28992:1', 'EPSG:28992:2', 'EPSG:28992:3', 'EPSG:28992:4', 'EPSG:28992:5', 'EPSG:28992:6', 'EPSG:28992:7', 'EPSG:28992:8', 'EPSG:28992:9', 'EPSG:28992:10', 'EPSG:28992:11', 'EPSG:28992:12', 'EPSG:28992:13', 'EPSG:28992:14']
    })
  })
});

var lufoLayer = new ol.layer.Tile({
  source: new ol.source.TileWMS({
    extend: [-2000.0, 290000.0, 294000.0, 630000.0],
    url: "https://service.pdok.nl/hwh/luchtfotorgb/wms/v1_0",
    params: {
      LAYERS: 'Actueel_orthoHR',
      TILED: "true"
    }
  })
});

// icon Layer
const unselectIcon = new ol.style.Style({
  image: new ol.style.Icon({
    src: './static/icons/location_sign_orange.svg',
    scale: 0.05,
    anchor: [0.5, 1],
  }),
});

// icon Layer
const selectIcon = new ol.style.Style({
  image: new ol.style.Icon({
    src: './static/icons/location_sign_red.svg',
    scale: 0.05,
    anchor: [0.5, 1],
  }),
});

// keep track of highlighted feature
var highlightedFeature = null;

// reset highlight
function reset_highlight(){
  if (highlightedFeature) {
  highlightedFeature.setStyle([unselectIcon])
}};

function initializeDateRangeSlider(fotoLayer) {
  var slider = document.getElementById('date-range-slider');

  // minDate and maxDate from fotos.js
  var minDateTime = minDate.getTime();
  var maxDateTime  = maxDate.getTime();

  // create slider
  noUiSlider.create(slider, {
    start: [minDateTime, maxDateTime],
    connect: true,
    range: {
        'min': minDateTime,
        'max': maxDateTime
    },
    tooltips: true,
    step: 86400000, // 1 day in milliseconds
    format: {
        to: function(value) {
            let date = new Date(parseInt(value));
            return date.toLocaleDateString('nl-NL');
        },
        from: function(value) {
            return parseInt(value);
        }
    }
  });

  slider.noUiSlider.on('update', function(values, handle) {
    var minDate = new Date(values[0].split('-').reverse().join('/'));
    var maxDate = new Date(values[1].split('-').reverse().join('/'));

    filterFeaturesByDate(fotoLayer, minDate, maxDate);
  });
}

// Function to disable and endable the slider
function disableSlider() {
  var slider = document.getElementById('date-range-slider')
  slider.style.display = 'none';
  slider.setAttribute('disabled', true);
}

function enableSlider() {
  var slider = document.getElementById('date-range-slider')
  slider.style.display = 'block';
  slider.removeAttribute('disabled');
}


function initializeMap() {
  var fotoSource = new ol.source.Vector({
    features: new ol.format.GeoJSON().readFeatures(geoJsonObj, {
      featureProjection: 'EPSG:28992'
    })
  });

  var fotoLayer = new ol.layer.Vector({
    source: fotoSource,
    style: unselectIcon,
  });

  // Layer for the highlighted feature

  var highlightLayer = new ol.layer.Vector({
    source: new ol.source.Vector(),
    style: selectIcon
  });

  var maxExtent = [-285401.92, 22598.08, 595401.9199999999, 903401.9199999999];
  var view = new ol.View({
    center: [155000, 463000],
    zoom: 3.4,
    projection: projection,
    extent: maxExtent
  });

  const zoomControl = new ol.control.Zoom({
    className: 'custom-zoom'
  });

  // Initialize the map
  window.map = new ol.Map({
    controls: [zoomControl],
    layers: [brtWaterLayer, fotoLayer, highlightLayer],
    target: 'map',
    view: view
  });

  // Calculate the extent of all features in the source
  var extent = fotoSource.getExtent();

  // Fit the view to the extent of all features
  view.fit(extent, {
      size: window.map.getSize(),
      padding: [200, 200, 200, 200], // Optional padding
      maxZoom: 15 // Optional max zoom level
  });


// Click event for features in fotoLayer
map.on('singleclick', function(evt) {
  var closestFeature = null;
  var minDistance = Infinity;

  // Reset highlighted feature
  reset_highlight()

  // Endable slider
  enableSlider()

  // Loop through features at the clicked pixel to find the closest one
  map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
      if (layer === fotoLayer) {
          var distance = ol.coordinate.squaredDistance(evt.coordinate, feature.getGeometry().getCoordinates());
          if (distance < minDistance) {
              minDistance = distance;
              highlightedFeature = feature;
          }
      }
  });

  if (highlightedFeature) {
      // populate info-screen
      openInfo(highlightedFeature);

      // disable slider
      disableSlider()

      // Clear previous highlight
      var highlightSource = highlightLayer.getSource();
      highlightSource.clear() 

      // Add the closest feature to the highlight layer
      highlightSource.addFeature(highlightedFeature);

      // Apply the selectIcon style to the closest feature
      highlightedFeature.setStyle([selectIcon]);

      // Center map on highlighted feature
      var coordinates = highlightedFeature.getGeometry().getCoordinates();
      map.getView().setCenter(coordinates);
  }
});

  // Initialize the date range slider
  initializeDateRangeSlider(fotoLayer);

}

// Force layer redraw
function forceLayerRedraw(layer) {
  var visible = layer.getVisible();
  layer.setVisible(!visible);
  layer.setVisible(visible);
}

function filterFeaturesByDate(fotoLayer, minDate, maxDate) {
  var source = fotoLayer.getSource();
  var features = source.getFeatures();

  features.forEach(function(feature) {
    var featureDateTime = new Date(feature.get('date_time'));

    if (featureDateTime >= minDate && featureDateTime <= maxDate) {
      feature.setStyle([greyIcon]);
    } else {
      feature.setStyle(new ol.style.Style(null));
    }
  });

  // Force layer redraw
  forceLayerRedraw(fotoLayer);
}

// Execute the function when the page is fully loaded
document.addEventListener("DOMContentLoaded", function() {
  initializeMap();
});

