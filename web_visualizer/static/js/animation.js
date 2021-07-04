// A Speed is an Integer, [1-100]
// INTERPRETATION: A Speed of _speed_ represents of _speed_ iterations per second

// animate : Data Data Map -> _
// Using the _client_ & _server_ data retrieved upon the request, animates the routes on _map_

async function animate(client_data, server_data, map) {
  // Turn off gesture handling and zoom control
  // map.set("gestureHandling", "none");
  // map.set("zoomControl", false);

  let destination = {
    "type": "router",
    "ip": server_data.ip_details.ip,
    "latitude": server_data.ip_details.latitude,
    "longitude": server_data.ip_details.longitude
  }

  destinationPosition.lat = parseFloat(destination.latitude);
  destinationPosition.lng = parseFloat(destination.longitude);

  destinationMarker = new google.maps.Marker({
    position: destinationPosition,
    map,
    icon: icons["server"].icon,
    title: "Destination location",
  });
  // Add the marker to the map
  destinationMarker.setMap(map);

  const numPackets = $('input#num-packets').val()
  
  // Generate and animate routes in both directions
  await animate_routes("request", numPackets, map);
  await animate_routes("response", numPackets, map);
}

// aniamte_routes : Direction Integer Map -> _
// Generates and animates all the routes in a particular _direction_
async function animate_routes(direction, num_routes, map) {
  // Use natural # template to aid with asynchronous recursion
  if (num_routes <= 0) {
    return;
  } else {
    return new Promise(function(resolve, reject) {
      $.getJSON(
        $SCRIPT_ROOT + "/routes", 
        { direction }, 
        function(route) {
          // First, animate the current route generated
          animate_route(route, map).then(() => {
            // Next animate the rest ouf the routes
            animate_routes(direction, num_routes - 1, map)
            // Finally, notify that the funciton is finished
              .then(resolve);
          })
        }
      ); 
    });

  }
}

// animate_route : [List-of Router] Map -> _
// Animates _route_ on _map_ by drawing lines at the current speed of the slider
async function animate_route(route, map) {

  return new Promise(function(resolve, reject) {
    let lines = [];

    // animate_line : Integer -> _
    // Animates the line at _index_ of route
  
    const animate_line = (index) => {
      const speed = $('input#speed').val()
  
      // We have finished the route animation
      if (index == route.length - 1) {
        clear_lines(lines);
        resolve();
        return;
      }
      
      else {
        lines.push(draw_line(route[index], route[index + 1], map))
        setTimeout(() => {
          animate_line(index + 1);
        }, 1000/speed)
      }
  
    }
  
    animate_line(0);
  })

}

// draw_line : Router Router Map -> Path
// Draw a line between _r1_ and _r2_ on _map_
function draw_line(r1, r2, map) {
  const path = [
    { lat: parseFloat(r1.latitude), lng: parseFloat(r1.longitude) },
    { lat: parseFloat(r2.latitude), lng: parseFloat(r2.longitude) }
  ];
  const line = new google.maps.Polyline({
    path,
    geodesic: true,
    strokeColor: '#FF0000',
    strokeOpacity: 1.0,
    strokeWeight: 1
  })
  line.setMap(map);
  return line;
}

function clear_lines(lines) {
  lines.forEach(line => {
    line.setMap(null);
  })
}