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
        0.420
      ],
      matrixIds: ['EPSG:28992:0', 'EPSG:28992:1', 'EPSG:28992:2', 'EPSG:28992:3', 'EPSG:28992:4', 'EPSG:28992:5', 'EPSG:28992:6', 'EPSG:28992:7', 'EPSG:28992:8', 'EPSG:28992:9', 'EPSG:28992:10', 'EPSG:28992:11', 'EPSG:28992:12', 'EPSG:28992:13']
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

// Search layer
const iconStyle = new ol.style.Style({
  image: new ol.style.Icon({
    src: './static/icons/location_sign_red.svg',
    scale: 0.05,
    anchor: [0.5, 1],
  }),
});

const labelStyle = (feature) => {
  return new ol.style.Style({
    text: new ol.style.Text({
      // text: feature.get("naam"),
      textAlign: "right",
      offsetY: 0,
      offsetX: -20,
      fill: new ol.style.Fill({
        color: 'black',
      }),
      font: '14px Calibri,sans-serif',
      stroke: new ol.style.Stroke({
        color: 'white',
        width: 1,
      }),
    }),
  });
};

function styleFunction(feature) {
  return [iconStyle, labelStyle(feature)];
}

function initializeMap() {
  var fotoSource = new ol.source.Vector({
    features: new ol.format.GeoJSON().readFeatures(geoJsonObj, {
      featureProjection: 'EPSG:28992'
    })
  });

  var fotoLayer = new ol.layer.Vector({
    source: fotoSource,
    style: styleFunction,
  });

  var view = new ol.View({
    center: [155000, 463000],
    zoom: 3.4,
    projection: projection
  });

  const zoomControl = new ol.control.Zoom({
    className: 'custom-zoom'
  });

  // Initialize the map
  window.map = new ol.Map({
    controls: [zoomControl],
    layers: [brtWaterLayer, fotoLayer],
    target: 'map',
    view: view
  });

  // Click event for features in fotoLayer
  map.on('singleclick', function (evt) {
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      var fotoUrl = feature.get('url');
      if (fotoUrl) {
        openInfo(fotoUrl);
      }
    });
  });

}



// Execute the function when the page is fully loaded
document.addEventListener("DOMContentLoaded", function() {
  initializeMap();
});

