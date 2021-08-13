
// CONSTANTS

const ZOOM = 3;
const ROUTER_SIZE = 15;
const INITIAL_NUM_ROUTERS = 1000;
const oceanicCables =
  "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/cable/cable-geo.json";
const PACKET_PATH = "M2.941 8c-2.941 0-1.47.779 0 1.974l22.059 16.789 22.059-16.737c1.472-1.195 2.941-2.026 0-2.026h-44.118zm-2.941 3.946v24.728c0 1.455 1.488 3.326 2.665 3.326h44.67c1.178 0 2.665-1.871 2.665-3.326v-24.728l-25 19.075-25-19.075z";

// VARIABLES

var animation_flag = true;
var auto_focus = false;
var random_router_choice = false;
var userPosition = {}
var destinationPosition = {}
let points;

// GRAPHICS

var map, userMarker, destinationMarker, routerMarkerImage, landingPointMarkerImage;
var packetSymbol = {};
const loadingSpinner = document.querySelector(".spinner-container");

const icons = {
  client: {
    icon: "static/images/client.png",
  },
  server: {
    icon: "static/images/server.png"
  },
  router: {
    icon: "static/images/router.png"
  },
  landingPoint: {
    icon: "static/images/landing_point.png"
  }
};

// Info windows
var clientInfo = {};



