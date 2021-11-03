// initialize the map
var map = L.map('map').setView([1, 1], 2);
var myGeoJSONPath = 'maps/world50.geo.json';

// load a tile layer
L.tileLayer('https://api.mapbox.com/styles/v1/lachainone/ckvj90z6yi8b715r0c3esa3qw/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoibGFjaGFpbm9uZSIsImEiOiJja3QzcjZ4czMwYThmMnBvMnNqb2lubTFnIn0.U1_7NA3wx8gzICYzro--iA', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibGFjaGFpbm9uZSIsImEiOiJja3Qzcmg4cXEwd3ViMnBwaDMwNGF1cmoxIn0.u0lEXBIE00yafHAc5FY1Vg'
}).addTo(map);

// load GeoJSON from an external file
$.getJSON(myGeoJSONPath,function(data){
  // add GeoJSON layer to the map once the file is loaded
 L.geoJson(data).addTo(map);
});