// A Speed is an Integer, [1-100]
// INTERPRETATION: A Speed of _speed_ represents of _speed_ iterations per second

function stop_animation() {
  ANIMATION_FLAG = false;
  document.querySelector("#controller").classList.remove("d-none");
  document.querySelector("#animation-options").classList.add("d-none");

  
}

// animate : Data Data Map -> _
// Using the _client_ & _server_ data retrieved upon the request, animates the routes on _map_

async function animate(client_data, server_data, map) {
  document.querySelector("#controller").classList.add("d-none");
  document.querySelector("#animation-options").classList.remove("d-none");

  ANIMATION_FLAG = true;

  display_server(server_data, map);

  serverInfo = new google.maps.InfoWindow({
    content: ""
  });

  serverInfo.open({
    anchor: destinationMarker,
    map,
    shouldFocus: false
  });

  destinationMarker.addListener('click', () => {
    serverInfo.open({
      anchor: destinationMarker,
      map,
      shouldFocus: false
    });
  });


  const numPackets = $('input#num-packets').val();
  
  // Generate and animate routes in both directions
  await animate_routes("request", numPackets, [], map, 0, client_data, server_data, numPackets);

  clientInfo = new google.maps.InfoWindow({
    content: ""
  });

  serverInfo.close();

  clientInfo.open({
    anchor: userMarker,
    map,
    shouldFocus: false
  })

  userMarker.addListener('click', () => {
    clientInfo.open({
      anchor: destinationMarker,
      map,
      shouldFocus: false
    });
  });


  await animate_routes("response", numPackets, [], map, 0, client_data, server_data, numPackets);

  clientInfo.close();

  stop_animation();
}

function display_server(server_data, map) {
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
}

// Update the info windows of client & server info such that they reflect the current state
// Callled when any packet is received
function update_client_info(client_data, server_data, packets_received, total_packets) {
  const content = `
  <div id="client-info-window" class="text-dark">
    <p>Packets Received: &nbsp;${packets_received}/${total_packets}</p>
    <h5 class="text-primary">Client Info</h5>
    <ul>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">IP</span>: &nbsp;${client_data.ip_details.ip}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">City</span>: &nbsp;${client_data.ip_details.city}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">Region</span>: &nbsp;${client_data.ip_details.region}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">Country</span>: &nbsp;${client_data.ip_details.country}
      </li>
    </ul>
    <h5 class="text-primary">Response Details</h5>
    <ul>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Return IP</span>: &nbsp;${server_data.ip_details.ip}</li>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Content Type</span>: &nbsp;${server_data.response_details.content_type}</li>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Status Code</span>: &nbsp;${server_data.response_details.status_code}</li>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Response URL</span>: &nbsp;${server_data.response_details.response_url}</li>
    </ul>
  </div>
`;
  clientInfo.setContent(content);
}

function update_server_info(client_data, server_data, packets_received, total_packets) {
  console.log(client_data, server_data);
  const content = `
  <div id="server-info-window" class="text-dark">
    <p>Packets Received: &nbsp;${packets_received}/${total_packets}</p>
    <h5 class="text-primary">Server Info</h5>
    <ul>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">IP</span>: &nbsp;${server_data.ip_details.ip}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">City</span>: &nbsp;${server_data.ip_details.city}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">Region</span>: &nbsp;${server_data.ip_details.region}
      </li>
      <li class="text-dark">
        <span class="text-dark" style="text-decoration: underline;">Country</span>: &nbsp;${server_data.ip_details.country}
      </li>
    </ul>
    <h5 class="text-primary">Request Details</h5>
    <ul>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Return IP</span>: &nbsp;${client_data.ip_details.ip}</li>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Method</span>: &nbsp;${client_data.request_details.request_method}</li>
      <li class="text-dark"><span class="text-dark" style="text-decoration: underline;">Request URL</span>: &nbsp;${client_data.request_details.request_url}</li>
    </ul>
  </div>
`;
  serverInfo.setContent(content);
}

// aniamte_routes : Direction Integer Map -> _
// Generates and animates all the routes in a particular _direction_
async function animate_routes(direction, num_routes, lines, map, packet_number, client_data, server_data, total_packets) {
  if (direction == "request")
    update_server_info(client_data, server_data, packet_number, total_packets);
  else
    update_client_info(client_data, server_data, packet_number, total_packets)
  // Use natural # template to aid with asynchronous recursion
  if (num_routes <= 0) {
    setTimeout(() => {
      clear_lines(lines);
      console.log("Cleared first routes")
    }, 100);
    return;
  } else {

    return new Promise(function(resolve, reject) {
      $.getJSON(
        $SCRIPT_ROOT + "/routes", 
        { direction }, 
        function(route) {
          if (ANIMATION_FLAG) {
                      // First, animate the current route generated
          animate_route(route, map).then((route_lines) => {
            // Next animate the rest ouf the routes
            animate_routes(direction, num_routes - 1, lines.concat(route_lines), map, packet_number + 1, client_data, server_data, total_packets)
            // Finally, notify that the funciton is finished
              .then(resolve);
          });
          } else {
            clear_lines(lines);
            resolve();
          }

        }
      ).fail(handleError);
    });
  }
}

// animate_route : [List-of Router] Map -> _
// Animates _route_ on _map_ by drawing lines at the current speed of the slider
async function animate_route(route, map) {

  return new Promise(function(resolve, reject) {
    let lines = [];
    let blurred_lines = [];
    
    let color = random_color();

    // [Helper] animate_connection : Integer -> _ 
    // Animates the connection (either a line or Polyline) at _index_ of route

    const animate_connection = (index) => {
      const speed = $('input#speed').val();
      let line, blurred_line;
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
          
          line = draw_line(path, color, map, speed, false);
          blurred_line = draw_line(path, color, map, speed, true);
          lines.push(line);
          blurred_lines.push(blurred_line);

          // After a short wait, animate the next connection
          if (ANIMATION_FLAG) {
            setTimeout(() => {
              animate_connection(index+1);
            }, 1000/speed)
          } else {
        clear_lines(lines);
            resolve(blurred_lines);
          }
        }


      }
    }
    if (ANIMATION_FLAG)
      animate_connection(0);
    else
      resolve([])
  })

}


// draw_line : Router Router Color Map Boolean -> Path
// Draw a line on _map_ using a given _path_, dependent on if the line is _blurred_
function draw_line(path, color, map, speed, blurred) {

  const line = new google.maps.Polyline({
    path,
    geodesic: false,
    strokeColor: color,
    strokeOpacity: blurred ? 0.5 : 1.0,
    strokeWeight: blurred ? 2 : 3,
  });

  if (blurred) {
    line.setMap(null);
  } else {
    line.setMap(map);
    animate_packet(line, speed, path, map);
  }
  return line;
}

// Adjust the offset from 0 to 100% in 1000/speed
function animate_packet(line, speed, path, map) {
  line.set("icons", [
    {
      icon: packetSymbol,
      offset: "0%"
    }
  ]);

  // Need to lengthen intervals
  let total_time = 1000/speed;
  let time_per_interval = 25;
  let num_intervals = total_time/time_per_interval;
  let offset = 0;
  const interval = window.setInterval(() => {
    offset += 100/num_intervals;
    const icons = line.get("icons");

    icons[0].offset = offset + "%";
    line.set("icons", icons);

    if (AUTO_FOCUS)
      set_center(path, offset, map);

    if (offset >= 100) {
      window.clearInterval(interval);
      line.set("icons", []);
    }
  }, time_per_interval)
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

// set_center : [List-of Coordinate] Number Map -> _
// Sets the center position of the map, at _offset_% between the first and last coordinate of path
function set_center(path, offset, map) {

  const determine_middle = (a, b) => a + (b - a) * offset/100;

  const start_coord = path[0];
  const end_coord = path[path.length - 1];

  const lat = determine_middle(start_coord.lat, end_coord.lat);
  const lng = determine_middle(start_coord.lng, end_coord.lng);

  map.setCenter(new google.maps.LatLng(lat, lng));
}