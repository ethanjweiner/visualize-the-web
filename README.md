# YOUR PROJECT TITLE
#### Video Demo:  https://www.youtube.com/watch?v=ybKiQPi6t5Q
#### Description:
Visualize the Web is an app that roughly simulates the geographic transmission of data across the Internet. Specifically, it visualizes possible routes that packets might take during a web request. Packets are small units of data into which a request is broken into. These packets are sent along a cable-path connecting some series of routers and landing points. A landing point is a special type of router on the coast that is used to send data overseas, to other landing points! The routers and landing points displayed on the map actually indicate the location of real routers with real IP addresses, randomly imported from a global database of routers and landing points. Visualize the Web lets you create your own request to some domain. Feel free to experiment with request options such as the "number of routers" and "number of packets" to animate, and make sure to read the legend to understand the symbols on the map.


Visualize the Web intends to show:

- that the Internet is really comprised of a system of routers connected by cables, not some arbitrary "cloud"
- the request-response model that all web requests follow
- that a singular web request is not sent as a singular chunk, but rather as a series of packets.
- that packets might take vastly different routes to travel to the same destination
- that data might need to travel in fiber optic cables overseas to reach its destination
- the geographic disparity in Internet usage across the world
- how amazing it is that this whole process occurs at lightning speed!

It is important to note that Visualize the Web is not a precise or accurate simulation of the web; it is only a representation. Some important clarifications to note are:

- Visualize the Web only displays a small number of routers. In reality, there are billions of routers worldwide.
- For animation purposes, Visualize the Web only displays a few packets per request. In reality, depending on the size of the request and response, there will be many more packets transmitted.
- The algorithm that Visualize the Web uses to route packets differs immensely from, and is much more simplistic than, the IP-based algorithm that real-world routers to route packets. - The routes that packets would actually take would be quite different.
- The transmission of data across the Internet occurs much faster than in Visualize the Web's simulation.