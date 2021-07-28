// timeout
// Create a timeout that is waited on to resolve

async function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// handleError : Data -> _
// Upon a server-side error, display an alert modal
function handleError(data) {
  // Display alert
  const alert = document.querySelector('.alert');
  if (!alert.classList.contains('show'))
    alert.classList.add('show');
  // Update alert content
  if (data.responseText) {
    alert.innerHTML = data.responseText;
  } else {
    alert.innerHTML = `
      <div class="error-styling">
        <h5>
            <span style="text-decoration: underline;"><span id="error-code">${data.code}</span> Error:</span> 
            <span id="error-name">${data.name}</span>       
        </h5>

        <p id="error-description">${data.description}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `
  }
}

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
    router_markers.push(new google.maps.Marker({
      position: coordinate,
      map,
      icon
    }));
}

// Deleting the routers

function deleteRouterMarkers() {
  clearRouterMarkers();
  router_markers = [];
}


function clearRouterMarkers() {
  setMapOnAll(null);
}

function setMapOnAll(map) {
  for (let i = 0; i < router_markers.length; i++) {
    router_markers[i].setMap(map);
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

// init_info_window
// Create an info window anchored at _anchor_
function init_info_window(anchor) {
  var infoWindow = new google.maps.InfoWindow({
    content: ""
  });

  infoWindow.open({
    anchor,
    map,
    shouldFocus: false
  });

  anchor.addListener('click', () => {
    infoWindow.open({
      anchor,
      map,
      shouldFocus: false
    });
  });

  return infoWindow
}

function random_color() {
  return "#" + Math.floor(Math.random() * 16777215).toString(16)
}

// set_center : [List-of Coordinate] Number Map -> _
// Sets the center position of the map, at _offset_% between the first and last coordinate of path
function set_center(path, offset) {

  const determine_middle = (a, b) => a + (b - a) * offset/100;

  const start_coord = path[0];
  const end_coord = path[path.length - 1];

  const lat = determine_middle(start_coord.lat, end_coord.lat);
  const lng = determine_middle(start_coord.lng, end_coord.lng);

  map.setCenter(new google.maps.LatLng(lat, lng));
}