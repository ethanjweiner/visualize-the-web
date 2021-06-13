// Constants
const ZOOM = 3;
const iconBase = "http://maps.google.com/mapfiles/kml/shapes/";
const icons = {
  home: {
    icon: "static/images/home-2.png",
  },
};

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
        displayRouters(map);
      },
      () => {
        handleLocationError(true, infoWindow, map.getCenter());
      }
    );
    // Browser doesn't supoprt geolocation
  } else {
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

// ROUTERS
updateRouters(map, 10);
// 1000 is an arbitrary number
// updateRouters(map, 1000);

// ANIMATION
$("#request-form").bind("submit", function (e) {
  e.preventDefault();
  // Run the request in "/animate", and retrieve the details needed to animate
  request_method = $("#get-radio").attr("checked") == "true" ? "GET" : "POST";
  console.log($());
  const requestData = {
    request_url: $('input[name="request-url"]').val(),
    request_method,
    request_content: $('textarea[name="request-content"]').val(),
  };

  $.getJSON(
    $SCRIPT_ROOT + "/animate",
    { request_data: requestData },
    function (responseData) {
      console.log("Response Data: ", responseData);
      animateMap(map, userMarker, requestData, responseData);
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
