
// Constants
const ZOOM = 3;
const ROUTER_SIZE = 15;
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
const INITIAL_NUM_ROUTERS = 1000;

var oceanicCables =
  "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/public/api/v2/cable/cable-geo.json";

var ROUTER_MARKERS = []

// Client & server positions
const userPosition = {}
const destinationPosition = {}
const packetSymbol = {}

// Info windows
var clientInfo = {};
var serverInfo = {};