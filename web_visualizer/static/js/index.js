// initMap
// Initializes the Google Maps API, displaying a static map
function initMap() {
  // If browser supports geolocation
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
          streetViewControl: false,
        });

        // Create a marker at the user's location
        userMarker = new google.maps.Marker({
          position: userPosition,
          map,
          icon: icons["client"].icon,
          title: "User location",
        });


        // Set the packet symbol
        packetSymbol = {
          strokeColor: "#000",
          path: PACKET_PATH,
          rotation: 180,
          anchor: new google.maps.Point(25, 20),
          scale: .5,
          fillColor: "#eddfab",
          fillOpacity: 1
        }

        // Load and display cables/routers
        loadCables(map);
        updateRouters(map, INITIAL_NUM_ROUTERS);

        // Listen for any changes
        initListeners(map);
      },
      () => {
        handleError({
          code: 500,
          name: "Geolocation error",
          description: "The Geolocation Service failed."
        })
      }
    );

  // Browser doesn't supoprt geolocation
  } else {
    handleError({
      code: 500,
      name: "Geolocation error",
      description: "Your browser doesn't support Geolocation."
    })
  }
}

// Event listeners
function initListeners(map) {
  // Update lat/lng
  map.addListener('mousemove', (mapsMouseEvent) => {
    document.querySelector("#coordinates").innerHTML = `
      Latitude: ${mapsMouseEvent.latLng.toJSON().lat.toFixed(3)}<br>
      Longitude: ${mapsMouseEvent.latLng.toJSON().lng.toFixed(3)}
    `;
  })
  
  // Sliders
  document.querySelector("#num-routers").addEventListener('input', (e) => {
    let num_routers = e.target.value * 100;
    document.querySelector("#num-routers-output").value = num_routers;
  });
  
  document.querySelector("#num-routers").addEventListener('mouseup', (e) => {
    let num_routers = e.target.value * 100;
    deleteRouterMarkers();
    updateRouters(map, num_routers)
  })

  document.querySelector("#num-packets").addEventListener('input', (e) => {
    let num_packets = e.target.value;
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
    document.querySelector('.alert').classList.remove('show');
    document.querySelector('input#speed').value = 1;

    // Remove the marker for the previous destination
    if (destinationMarker) destinationMarker.setMap(null);
  
    const request_data = {
      request_url: $('input[name="request-url"]').val(),
      request_method : document.querySelector("#get-radio").checked ? "GET" : "POST",
      request_content: $('textarea[name="request-content"]').val(),
      latitude: userPosition.lat,
      longitude: userPosition.lng
    };
  
    $.getJSON(
      $SCRIPT_ROOT + "/request",
      request_data,
      function (data) {
        animate(data.client_data, data.server_data, map);
      }
    ).fail(handleError);
  });

  document.querySelector("#stop-animation").addEventListener('click', (e) => {
    e.preventDefault();
    stop_animation();
  });

  document.querySelector('#auto-focus').addEventListener('input', () => {
    auto_focus = !auto_focus;
  });

}