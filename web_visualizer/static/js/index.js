// Determines whether to call animateMap()
const isAnimated =
  document.currentScript.getAttribute("animation") === "on" ? true : false;
let map, infoWindow, userMarker;

// initMap
// Initializes the Google Maps API, displays a static map, and animates if request was sent
function initMap() {
  // bIf rowser supports geolocation
  if (navigator.geolocation) {
    // Pan and mark user's location on load
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const center = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };

        map = new google.maps.Map(document.getElementById("map"), {
          center,
          zoom: ZOOM,
          gestureHandling: "greedy",
          zoomControl: true,
        });

        // Use for displaying errors
        infoWindow = new google.maps.InfoWindow();

        // Create a home marker at the user's location
        userMarker = new google.maps.Marker({
          position: center,
          map,
          icon: icons["home"].icon,
          title: "User location",
        });

        loadCables(map);
        // LOAD AND DISPLAY ROUTERS
        updateRouters(map, INITIAL_NUM_ROUTERS);
      },
      () => {
        handleLocationError(true, infoWindow, map.getCenter());
      }
    );
    // Add event listeners
    // Update the # of routers upon sliding
    document.querySelector("#num-routers").addEventListener('input', (e) => {
      // Multiply the slider value by 100
      let num_routers = e.target.value * 100;
      // Update the output element
      document.querySelector("#num-routers-output").value = num_routers;
    });

    document.querySelector("#num-routers").addEventListener('mouseup', (e) => {
      let num_routers = e.target.value * 100;
      deleteRouterMarkers();
      updateRouters(map, num_routers)
    })

        // Add event listeners
    // Update the # of routers upon sliding
    document.querySelector("#num-packets").addEventListener('input', (e) => {
      // Multiply the slider value by 100
      let num_packets = e.target.value;
      // Update the output element
      document.querySelector("#num-packets-output").value = num_packets;
    });

  // Browser doesn't supoprt geolocation
  } else {
    handleLocationError(false, infoWindow, map.getCenter());
  }
}



// ANIMATION
$("#request-form").bind("submit", function (e) {
  e.preventDefault();
  // Run the request in "/animate", and retrieve the details needed to animate
  request_method = $("#get-radio").attr("checked") == "true" ? "GET" : "POST";

  const request_data = {
    request_url: $('input[name="request-url"]').val(),
    request_method,
    request_content: $('textarea[name="request-content"]').val(),
    num_packets: $('input#num-packets').val()
  };

  $.getJSON(
    $SCRIPT_ROOT + "/routes",
    request_data,
    function (animationData) {
      console.log("Animation Data: ", animationData);
      // animateMap(map, userMarker, requestRoutes, responseRoutes, data)
    }
  );
  return false;
});

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? "Error: The Geolocation service failed."
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
}
