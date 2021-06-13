// animateMap : [Google Maps Map] [InfoMarker] -> _
// Creates the animation with the given map
// - Turn off gesture handling and zoom control
// - Run the animation

function animateMap(map, userMarker, requestData, responseData) {
  console.log(requestData, responseData);

  // Turn off gesture handling and zoom control
  map.set("gestureHandling", "none");
  map.set("zoomControl", false);
}
