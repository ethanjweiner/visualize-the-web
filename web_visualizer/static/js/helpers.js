// timeout
// Create a timeout that waits _ms_ to resolve
async function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// handleError : Data -> _
// Upon an error with _data_, display an alert modal
function handleError(data) {
  stop_animation();
  // Display alert
  const alert = document.querySelector('.alert');
  if (!alert.classList.contains('show'))
    alert.classList.add('show');
  // Update alert content
  if (data.responseText) {
    alert.innerHTML = data.responseText;
  } else {
    alert.innerHTML = `
      <div class="error-styling">
        <h5>
            <span style="text-decoration: underline;"><span id="error-code">${data.code}</span> Error:</span> 
            <span id="error-name">${data.name}</span>       
        </h5>

        <p id="error-description">${data.description}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `
  }
}

// Radios

const getRadio = document.querySelector("#get-radio");
const postRadio = document.querySelector("#post-radio");

postRadio.addEventListener("input", () => {
  toggleMethod();
});

getRadio.addEventListener("input", () => {
  toggleMethod();
});

function toggleMethod() {
  const body = document.querySelector("#request-content");
  if (body.classList.contains("d-none")) body.classList.remove("d-none");
  else body.classList.add("d-none");
}

// init_info_window : Marker -> _
// Create an info window anchored at _anchor_
function init_info_window(anchor) {
  var infoWindow = new google.maps.InfoWindow({
    content: ""
  });

  infoWindow.open({
    anchor,
    map,
    shouldFocus: false
  });

  anchor.addListener('click', () => {
    infoWindow.open({
      anchor,
      map,
      shouldFocus: false
    });
  });

  return infoWindow
}

// random_color : _ -> Color
// Generate a random hex color
function random_color() {
  return "#" + Math.floor(Math.random() * 16777215).toString(16)
}

// set_center : [List-of Coordinate] Number Map -> _
// Sets the center position of the map, at _offset_% between the first and last coordinate of path
function set_center(path, offset) {

  const determine_middle = (a, b) => a + (b - a) * offset/100;

  const start_coord = path[0];
  const end_coord = path[path.length - 1];

  const lat = determine_middle(start_coord.lat, end_coord.lat);
  const lng = determine_middle(start_coord.lng, end_coord.lng);

  map.setCenter(new google.maps.LatLng(lat, lng));
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


// EVENT LISTENERS
// Initializes all event listeners (once the map is loaded)
function initListeners() {
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
    points.delete_points().generate_points(num_routers);
  })

  document.querySelector("#num-packets").addEventListener('input', (e) => {
    let num_packets = e.target.value;
    document.querySelector("#num-packets-output").value = num_packets;
  });
  
  // Listen for request
  $("#request-form").bind("submit", function (e) {
    e.preventDefault();
    document.querySelector('.alert').classList.remove('show');
    document.querySelector('input#speed').value = 1;

    // Remove the marker for the previous destination
    if (destinationMarker) destinationMarker.setMap(null);

    var request_details;

    request_details = {
      is_random: random_router_choice,
      num_routers: points.num_routers,
      request_url: $('input[name="request-url"]').val(),
      request_method : document.querySelector("#get-radio").checked ? "GET" : "POST",
      request_content: $('textarea[name="request-content"]').val(),
      latitude: userPosition.lat,
      longitude: userPosition.lng
    };
  
    start_animation();

    $.post(
      $SCRIPT_ROOT + "/request",
      { request_details: JSON.stringify(request_details) },
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