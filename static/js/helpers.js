// Add a body parameter for post requests
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
// Generates and displays markers on _map_
function updateRouters(map, num_routers) {
  // Retrieves the router locations for a particular # of routers
  $.getJSON(
    $SCRIPT_ROOT + "/routers",
    { num_routers },
    function (routers) {
      console.log(routers);
      displayRouters(map, routers);
    }
  );
}

// displayRouters : [Google Maps Map] [List-of Routers] -> _
// Superimposes router icons on _map_ at the locations specified by _coordinates_
function displayRouters(map, routers) {
  // Display
}
