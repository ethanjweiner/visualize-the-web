var map, infoWindow, userMarker, destinationMarker;

// initMap
// Initializes the Google Maps API, displaying a static map
function initMap() {
  // If rowser supports geolocation
  if (navigator.geolocation) {
    // Pan and mark user's location on load
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userPosition.lat = position.coords.latitude;
        userPosition.lng = position.coords.longitude;

        map = new google.maps.Map(document.getElementById("map"), {
          center: userPosition,
          zoom: ZOOM,
          gestureHandling: "greedy",
          zoomControl: true,
        });

        // Create a home marker at the user's location
        userMarker = new google.maps.Marker({
          position: userPosition,
          map,
          icon: icons["client"].icon,
          title: "User location",
        });

        // Packet symbol
        packetSymbol.strokeColor = "#000"
        packetSymbol.path = "M2.941 8c-2.941 0-1.47.779 0 1.974l22.059 16.789 22.059-16.737c1.472-1.195 2.941-2.026 0-2.026h-44.118zm-2.941 3.946v24.728c0 1.455 1.488 3.326 2.665 3.326h44.67c1.178 0 2.665-1.871 2.665-3.326v-24.728l-25 19.075-25-19.075z"
        packetSymbol.rotation = 180;
        packetSymbol.anchor = new google.maps.Point(25, 20);
        packetSymbol.scale = .5;
        packetSymbol.fillColor = "#eddfab";
        packetSymbol.fillOpacity = 1;

        // Load and display cables/routers
        loadCables(map);
        updateRouters(map, INITIAL_NUM_ROUTERS);

        initListeners(map);
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

// Event listeners

function initListeners(map) {
  // Update lat/lng
  map.addListener('mousemove', (mapsMouseEvent) => {
    document.querySelector("#coordinates").innerHTML = `
      Latitude: ${mapsMouseEvent.latLng.toJSON().lat}<br>
      Longitude: ${mapsMouseEvent.latLng.toJSON().lng}
    `;
  })
  
  // Sliders
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
  // Update the # of routers upon sliding
  document.querySelector("#num-packets").addEventListener('input', (e) => {
    // Multiply the slider value by 100
    let num_packets = e.target.value;
    // Update the output element
    document.querySelector("#num-packets-output").value = num_packets;
  });
  
  // Coordinate form  
  $('#coord-form').bind("submit", function(e) {
    e.preventDefault()

    const latitude = parseFloat($('input[name="latitude"]').val())
    const longitude = parseFloat($('input[name="longitude"]').val())

    const marker = new google.maps.Marker({
      position: { lat: latitude, lng: longitude },
      map
    })

    marker.setMap(map);
  })
  
  // Listen for request
  $("#request-form").bind("submit", function (e) {
    e.preventDefault();
    // Remove the marker for the previous destination
    if (destinationMarker) destinationMarker.setMap(null);
    // Run the request in "/animate", and retrieve the details needed to animate
    request_method = $("#get-radio").attr("checked") == "true" ? "GET" : "POST";
  
    const request_data = {
      request_url: $('input[name="request-url"]').val(),
      request_method,
      request_content: $('textarea[name="request-content"]').val(),
      latitude: userPosition.lat,
      longitude: userPosition.lng
    };
  
    $.getJSON(
      $SCRIPT_ROOT + "/request",
      request_data,
      function (data) {
        animate(data.client_data, data.server_data, map)
      }
    );
  });
}


function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? "Error: The Geolocation service failed."
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
}
