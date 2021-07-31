// loadCables
// Statically displays all oceanic cables on _map_
function loadCables() {
  // Load and display fiber optic cable GeoJSON data
  map.data.loadGeoJson(oceanicCables);

  // Style the oceanic wires to be grey
  map.data.setStyle({
    strokeWeight: 1,
    strokeColor: "rgba(1, 1, 1, .2)",
  });
}
  
// Use this Points class to generate, display, & delete points
class Points {
  constructor(num_routers) {
    this.num_routers = num_routers;
    this.points = [];
    this.markers = [];
  }
  // generate_points
  // Generates all _num_routers_ routers and landing points by retrieving them from the server
  async generate_points(num_routers) {
    if (num_routers) {
      this.update_num_routers(num_routers);
    }
    document.getElementById("map").classList.add("d-none");
    // Retrieves all Router and LandingPoint locations
    $.getJSON(
      $SCRIPT_ROOT + "/routers",
      { num_routers: this.num_routers },
      (points) => {
        this.points = points;
        document.getElementById("map").classList.remove("d-none");
        this.display_points();
      }
    );

  }
  // display_points
  // Displays every point as a marker on the map, and stores these markers
  display_points() {

    const display_point = (point) => {

      this.markers.push(new google.maps.Marker({
        position: new google.maps.LatLng(point.latitude, point.longitude),
        map,
        icon: point.type == 'router' ? routerMarkerImage : landingPointMarkerImage
      }));

    }

    this.points.forEach(display_point);
    return this;

  }
  // delete_points
  // Removes all points from the display and clears the arrays
  delete_points() {
    this.markers.forEach(marker => {
      marker.setMap(null)
    })
    this.points = [];
    this.markers = [];
    return this;
  }

  update_num_routers(num) {
    if (!Number.isInteger(num) || num < 300 || num > 4000)
      throw new Error("The number of routers must be an integer between 300 and 4000.")
    this.num_routers = num;
    return this;
  }
}