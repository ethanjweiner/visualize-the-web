// loadCables : [Google Maps Map] -> _
// Statically displays all oceanic cables on _map_
function loadCables(map) {
  // Load and display fiber optic cable GeoJSON data
  map.data.loadGeoJson(oceanicCables);

  // Style the oceanic wires to be grey
  map.data.setStyle({
    strokeWeight: 1,
    strokeColor: "rgba(1, 1, 1, .2)",
  });
}

// generateMarkerContent
// Produces the content that will be contained in the animated InfoMarker representing the request or response
function generateMarkerContent() {}

// updateRouters : [Google Maps Map] Number -> _
// Generates and displays _num_routers_ markers on _map_ representing routers
function updateRouters(map, num_routers) {
  // Retrieves the router locations for a particular # of routers
  $.getJSON(
    $SCRIPT_ROOT + "/routers",
    { num_routers },
    function (routers) {
      displayRouters(map, routers);
    }
  );
}

// Displaying the routers

// displayRouters : [Google Maps Map] [List-of Routers] -> _
// Superimposes router icons on _map_ at the locations specified by _coordinates_
function displayRouters(map, routers) {

  const routerMarkerImage = new google.maps.MarkerImage(
    icons["router"].icon,
    new google.maps.Size(15,15),
    null,
    null,
    new google.maps.Size(15,15)
  );
  
  const landingPointMarkerImage = new google.maps.MarkerImage(
    icons["landingPoint"].icon,
    new google.maps.Size(15,15),
    null,
    null,
    new google.maps.Size(15,15)
  );


  routers.forEach(router => {
    let image = router.type == 'router' ? routerMarkerImage : landingPointMarkerImage;
    displayRouter(map, router, image);
  });

}

// displayRouter : [Google Maps Map] Router Image -> _
// Displays a singular _router_ on the map, whose icon is dependent on the type of router
function displayRouter(map, router, icon) {
    // Create a Google Maps Coordinate for that router
    const coordinate = new google.maps.LatLng(router.latitude, router.longitude)

    // Display a marker at that coordinate
    // Save the router in an array, in case it is used later in the animation
    ROUTER_MARKERS.push(new google.maps.Marker({
      position: coordinate,
      map,
      icon
    }));
}

// Deleting the routers

function deleteRouterMarkers() {
  clearRouterMarkers();
  ROUTER_MARKERS = [];
}


function clearRouterMarkers() {
  setMapOnAll(null);
}

function setMapOnAll(map) {
  for (let i = 0; i < ROUTER_MARKERS.length; i++) {
    ROUTER_MARKERS[i].setMap(map);
  }
}

function showRouterMarkers() {
  setMapOnAll(map);
}

// Additional helpers

const getRadio = document.querySelector("#get-radio");
const postRadio = document.querySelector("#post-radio");

postRadio.addEventListener("input", () => {
  toggleMethod();
});

getRadio.addEventListener("input", () => {
  toggleMethod();
});

function toggleMethod() {
  const body = document.querySelector("#request-content");
  if (body.classList.contains("d-none")) body.classList.remove("d-none");
  else body.classList.add("d-none");
}