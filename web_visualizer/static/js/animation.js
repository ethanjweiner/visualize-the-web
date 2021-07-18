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
    setTimeout(() => {
      clear_lines(lines);
      console.log("Cleared first routes")
    }, 3000);
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

  console.log(route)
  return new Promise(function(resolve, reject) {
    let lines = [];
    let blurred_lines = [];
    
    let color = random_color();

    // [Helper] animate_connection : Integer -> _ 
    // Animates the connection (either a line or Polyline) at _index_ of route

    const animate_connection = (index) => {
      const speed = $('input#speed').val()
      // We have finished the route animation
      
      if (index == route.length - 1) {
        clear_lines(lines);
        draw_lines(blurred_lines, map);
        // Provide the blurred lines & cables for animation
        resolve(blurred_lines);
      }
      // Part wof the route is left to animate
      else {
        let p1 = route[index];
        let p2 = route[index+1]

        // Skip this type of connection
        if (p2.type == "cable")
          animate_connection(index + 1)
        
        else {
          // Determine the path to draw
          let path = [];
          // If one node is a cable, draw the cable polyline
          if (p1.type == "cable") {
            if (p1.nodes.length)
              path = p1.nodes.map(node => { return { lat: node[1], lng: node[0] }}) 
            else
              path = [
                { lat: parseFloat(route[index-1].latitude), lng: parseFloat(route[index-1].longitude) },
                { lat: parseFloat(route[index+1].latitude), lng: parseFloat(route[index+1].longitude) }
              ]
          // Otherwise, draw a singular line between two routers
          } else {
            path = [
              { lat: parseFloat(p1.latitude), lng: parseFloat(p1.longitude) },
              { lat: parseFloat(p2.latitude), lng: parseFloat(p2.longitude) }
            ]
          }
          
          // Draw the polylines
          lines.push(draw_line(path, color, map, false));
          blurred_lines.push(draw_line(path, color, map, true));
        }

        // After a short wait, animate the next connection
        setTimeout(() => {
          animate_connection(index+1);
        }, 1000/speed)
      }
    }
    animate_connection(0);
  })

}


// draw_line : Router Router Color Map Boolean -> Path
// Draw a line on _map_ using a given _path_, dependent on if the line is _blurred_
function draw_line(path, color, map, blurred) {

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