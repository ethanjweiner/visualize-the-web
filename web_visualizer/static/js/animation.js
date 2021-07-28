// A Speed is an Integer, [1-20]
// INTERPRETATION: A Speed of _speed_ represents of _speed_ iterations per second

// animate : Data Data Map -> _
// Using the _client_ & _server_ data retrieved upon the request, animates the routes on _map_
async function animate(client_data, server_data) {
  start_animation();

  display_server(server_data);

  const numPackets = $('input#num-packets').val();
  
  // Generate and animate routes in both directions
  const routeAnimation = new RouteAnimation(client_data, server_data, numPackets);
  await routeAnimation.animate("request");
  await routeAnimation.animate("response");

  stop_animation();
}

// RequestAnimation
// Usage: Animate either the request or response between a client & server
class RouteAnimation {
  constructor(client_data, server_data, num_routes) {
    this.client_data = client_data;
    this.server_data = server_data;
    this.num_routes = num_routes;
  }
  async animate(direction) {
    // Initialize the content of the info window
    if (direction == "request")
      this.infoWindow = init_info_window(destinationMarker);
    else
      this.infoWindow = init_info_window(userMarker);

    // Animation logic
    await this.animate_routes(direction)

    // Close info window
    this.infoWindow.close()
  }

  update_info_window(direction, packet_number) {
    let content;
    if (direction == "request") {
      // Retrieve the server window template
      content = ""
    } else {
      // Retrieve the client window template
      content = ""
    }
    this.infoWindow.setContent(content);
  }
  // Initialize the animation of routes
  async animate_routes(direction) {
    await this.animate_routes_helper(direction, this.num_routes, [])
  }
  // ACCUMULATOR: _lines_ contains all lines drawn as part of the routes so far
  async animate_routes_helper(direction, num_routes, lines) {
    let packet_number = this.num_routes - num_routes; 
    this.update_info_window(direction, packet_number);

    if (num_routes == 0) {
      setTimeout(() => {
        console.log(lines);
        clear_lines(lines);
      }, 100);
      return;
    } else {
      // Return a promise to evoke asynchronous functionality
      return new Promise((resolve, reject) => {
        $.getJSON(
          $SCRIPT_ROOT + "/routes",
          { direction },
          (route) => {
            if (animation_flag) {
              this.animate_route(route).then((route_lines) => {
                this.animate_routes_helper(direction, num_routes - 1, lines.concat(route_lines))
                  .then(resolve)
              })
            } else {
              clear_lines(lines);
              resolve();
            }
          }
        ).fail(handleError);
      });
    }
  }
  async animate_route(route) {

    let lines = [];
    let blurred_lines = [];
    let color = random_color();

    const animate_connection = async (index) => {

      const cable_path = (cable) => {
        // Use the cable nodes
        if (cable.nodes.length)
          return cable.nodes.map(node => { return { lat: node[1], lng: node[0] }}) 
        // Else skip over the cable entirely
        else {
          return [
            { lat: parseFloat(route[index-1].latitude), lng: parseFloat(route[index-1].longitude) },
            { lat: parseFloat(route[index+1].latitude), lng: parseFloat(route[index+1].longitude) }
          ]
        }
          
      }
  
      const routers_path = (r1, r2) => {
        return [
          { lat: parseFloat(r1.latitude), lng: parseFloat(r1.longitude) },
          { lat: parseFloat(r2.latitude), lng: parseFloat(r2.longitude) }
        ]
      }
  
      const speed = $('input#speed').val();
  
      if (index == route.length - 1) {
        clear_lines(lines);
        draw_lines(blurred_lines);
        return;
      } else {
        let p1 = route[index];
        let p2 = route[index+1];
  
        // Skip to the cable connection
        if (p2.type == "cable")
          animate_connection(index + 1)
        else {
          let path = [];
          if (p1.type == "cable")
            path = cable_path(p1)
          else
            path = routers_path(p1, p2)
  
          lines.push(draw_line(path, color, false, speed));
          blurred_lines.push(draw_line(path, color, true, speed));
  
          if (animation_flag) {
            await timeout(1000/speed);
            return await animate_connection(index + 1);
          } else {
            clear_lines(lines);
            return blurred_lines;
          }
        }
      }
    }

    if (animation_flag) {
      await animate_connection(0);
      return blurred_lines;
    }
    else
      return [];
  }
}

// Drawing helpers

// draw_line : Router Router Color Map Boolean -> Path
// Draw a line on _map_ using a given _path_, dependent on if the line is _blurred_
function draw_line(path, color, blurred, speed) {

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
    animate_packet(line, speed, path);
  }
  return line;
}

// Adjust the offset from 0 to 100% in 1000/speed
function animate_packet(line, speed, path) {
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

    if (auto_focus)
      set_center(path, offset);

    if (offset >= 100) {
      window.clearInterval(interval);
      line.set("icons", []);
    }
  }, time_per_interval)
}

function draw_lines(lines) {
  lines.forEach(line => {
    line.setMap(map);
  })
}

function clear_lines(lines) {
  lines.forEach(line => {
    line.setMap(null);
  })
}

function display_server(server_data) {
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


function start_animation() {
  document.querySelector("#controller").classList.add("d-none");
  document.querySelector("#animation-options").classList.remove("d-none");
  animation_flag = true;
}

function stop_animation() {
  animation_flag = false;
  document.querySelector("#controller").classList.remove("d-none");
  document.querySelector("#animation-options").classList.add("d-none");
}