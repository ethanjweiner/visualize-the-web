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
  await animate_routes("request", numPackets, [], map);
  await animate_routes("response", numPackets, [], map);
}

// aniamte_routes : Direction Integer Map -> _
// Generates and animates all the routes in a particular _direction_
async function animate_routes(direction, num_routes, lines, map) {
  // Use natural # template to aid with asynchronous recursion

  if (num_routes <= 0) {
    clear_lines(lines)
    return;
  } else {
    return new Promise(function(resolve, reject) {
      $.getJSON(
        $SCRIPT_ROOT + "/routes", 
        { direction }, 
        function(route) {
          // First, animate the current route generated
          animate_route(route, map).then((route_lines) => {
            // Next animate the rest ouf the routes
            animate_routes(direction, num_routes - 1, lines.concat(route_lines), map)
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
    let blurred_lines = []
    
    let color = random_color();

    // animate_line : Integer -> _
    // Animates the line at _index_ of route
  
    const animate_line = (index) => {
      const speed = $('input#speed').val()
  
      // We have finished the route animation
      if (index == route.length - 1) {
        clear_lines(lines);
        draw_lines(blurred_lines, map);
        resolve(blurred_lines);
      }
      
      else {
        lines.push(draw_line(route[index], route[index + 1], color, map, false));
        blurred_lines.push(draw_line(route[index], route[index + 1], color, map, true));

        setTimeout(() => {
          animate_line(index + 1);
        }, 1000/speed)
      }
  
    }
  
    animate_line(0);
  })

}

// draw_line : Router Router Color Map -> Path
// Draw a line between _r1_ and _r2_ on _map_, dependent on if the line is _blurred_
function draw_line(r1, r2, color, map, blurred) {
  const path = [
    { lat: parseFloat(r1.latitude), lng: parseFloat(r1.longitude) },
    { lat: parseFloat(r2.latitude), lng: parseFloat(r2.longitude) }
  ];
  const line = new google.maps.Polyline({
    path,
    geodesic: false,
    strokeColor: color,
    strokeOpacity: blurred ? 0.5 : 1.0,
    strokeWeight: blurred ? 2 : 3
  })
  if (blurred) {
    line.setMap(null);
  } else {
    line.setMap(map);
  }
  return line;
}

function draw_lines(lines, map) {
  lines.forEach(line => {
    line.setMap(map);
  })
}

function clear_lines(lines) {
  lines.forEach(line => {
    line.setMap(null);
  })
}

function blur_lines(lines, map) {
  let blurred_lines = []
  // Draw the blurred lines
  lines.forEach(line => {
    // Add a new line with a lower stroke opacity
    console.log(line, line.path, line.geodesic)
    blurred_lines.push(new google.maps.Polyline({
      path: line.path,
      geodesic: false,
      strokeColor: line.strokeColor,
      strokeOpacity: 0.5,
      strokeWeight: 3
    }));
  })

  blurred_lines.forEach(blurred_line => {
    blurred_line.setMap(map);
  })

  // Remove the previously drawn lines
  clear_lines(lines);

  return blurred_lines;
}

function random_color() {
  return "#" + Math.floor(Math.random() * 16777215).toString(16)
}