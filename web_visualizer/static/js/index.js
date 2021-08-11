// initMap
// Initializes the Google Maps API, displaying a static map with a marker for the user, oceanic cables, and routers
// Initializes all event listeners pertaining to the map
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

        routerMarkerImage = new google.maps.MarkerImage(
          icons["router"].icon,
          new google.maps.Size(15,15),
          null,
          null,
          new google.maps.Size(15,15)
        );

        landingPointMarkerImage = new google.maps.MarkerImage(
          icons["landingPoint"].icon,
          new google.maps.Size(15,15),
          null,
          null,
          new google.maps.Size(15,15)
        );

        // Load and display cables/routers
        loadCables();

        points = new Points(INITIAL_NUM_ROUTERS);
        points.generate_points();

        // Initialize all event listeners
        initListeners();
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

loadModal();