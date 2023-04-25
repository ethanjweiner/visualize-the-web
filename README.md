# Visualize the Web

**Visualize the Web** is an app that roughly simulates the geographic transmission of data across the Internet. Specifically, it visualizes possible routes that packets might take during a web request. Packets are small units of data into which a request is broken into. These packets are sent along a cable-path connecting some series of routers and landing points. A landing point is a special type of router on the coast that is used to send data overseas, to other landing points! The routers and landing points displayed on the map actually indicate the location of real routers with real IP addresses, randomly imported from a global database of routers and landing points. Visualize the Web lets you create your own request to some domain. Feel free to experiment with request options such as the "number of routers" and "number of packets" to animate, and make sure to read the legend to understand the symbols on the map. Watch the [video demo](https://www.youtube.com/watch?v=ybKiQPi6t5Qmore) for more information.

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

#### File Explanations

- *__init__.py* and *setup.py* initialize and configures the application and database on the server. It specifies the main route and uses a Javascript bundler to package all javascript into a singular "bundle.js" file. Setup.py specifies the required packages used in the application.
- *data/points.db* is the home of the SQLite3 database, storing "points" (routers and landing points) in one table and "paths" (two-way paths between continents that I generated) in another. I use an object-relation-mapper to provide class definitions in Python code that map directly to these two tables. Routers and landing points inherit the points class, and so in the points.db they are both represented as points, but with a few differing properties. Points.db contains thousands of routers that are based on the location of real ip addresses. These real ip addresses were retrieved from an outside geolocation database at "https://db-ip.com". The landing points, and associated cables, were retrieved from a separate geolocation database at "https://submarine-cable-map-2021.telegeography.com/". 
- *py_main/routers.py* is called upon loading the application to select a sample of routers from "points.db". This sample is displayed on the map to the client, and the id of the first router is stored in a session so that the sample of routers can later be accessed again (via that id) in the routing algorithm.
- *py_main/request.py* is the backbone of any simulated request made from the client. It actually makes the request that the client inputted, and gathers all the resulting information about the client and server, returning it to the browser for display on the map. In particular, it uses the "ip_info" library to gather location information corresponding to the local and server ip addresses. It also stores the client and server data in a session so that it can be used in the "route" route.
- *py_main/route.py* initializes the routing procedure, from the client to server and back.
- *py_main/classes.py* is the meat of Web Visualizer. It contains the aforementioned object-relational-mapping classes that correspond directly to the database entries. But more importantly, it contains the detailed, recursive, greedy-best-first-search-inspired routing algorithms that direct one router to the next, accumulating a path along the way. It also contains a more specific DFS-inspired algorithm used to construct the pathway that a packet will take along an oceanic cable.
- *py_auxiliary/helpers.py* contains commonly used helpers, including distance (which uses the Harversine formula to compute the distance between two geographic coordinates), choose_point + generate_probabilities + get_weight (used in the routing algorithms to randomly choose a nearby point), random_radius (randomly generate a search radius for the routing algorithm), and random_router_seed (retrieves a random router id from "points.db")
- *py_auxiliary/constants.py* contains various constants used to support the routing algorithm, including file pathways, maximum routing time, and the maximum number of routers that can be included in a singular path/route/
- *py_auxiliary/error_handler.py* is meant to serve as a global server-side error handler that provides an HTML error message template to render as an alert.
- *static/js/index.js* configures the setup of the map (with overlays such as the client icon, server icon, oceanic cables) and gloabl client-side error handling.
- *static/js/animation.js* contains all the code used to animate a route. It defines a RouteAnimation class that encapsulates all information associated with a request needed for animating. It asynchronously calls the "/route" route to generate the routes (both ways), and then displays those routes consecutively by drawing lines while simultaneously moving a packet icon in tandem with those lines.
- *static/js/helpers.js* contains commonly used helpers, including timeout (used to halt a block of code in place for animation purposes), an error handler, init_info_window and info_window_content (construct an info window to see client and server data), set_center (sets the center position of the map at the current location of the packet), start_animation, stop_animation, init_listeners (initialize all event listeners), zoom_to_bounds (uses coordinates to find the bounds of the visible portion of the map)
- *static/js/init_display.js* provides the functionality to load the oceanic cables, routers, and landing points onto the map upon load. It provides a "Points" class that is used to specifically request and display a sample of routers from "points.db". 
- *static/js/globals.js* provides various globals: constants, global variables, and graphics constants.
- *templates/* contains all the templates created using Jinja syntax, including index.html (the main template), the about modal, animation options controller, the left sidebar controller, and an error alert.
- *static/js/styles.css* defines all the style rules in the app not already defined by Bootstrap classes.

#### Design Choices:

1. **Object-oriented approach**: While the app as a whole combines object-oriented and functional programming principles, I decided to take a more object-oriented approach for the meat of this application. The points, cables, and pathways are all represented by objects. This made complete sense since I was using Flask-SQLAlchemy, an object-relation-mapper database whose goal is to represent database rows with objects (models) in Python code. Since the routing algorithms have a very recursive, self-referential nature, I defined the routing algorithms themselves as part of these models. 

2. **Greedy BFS**: The biggest problem (by far) that this project needed to solve was determining how to create a path from a large set of unconnected points. I had to consider questions such as:
  - How will routing overseas take place?
  - How will I create realistic paths?
  - How can I make sure that all packets don't take the same path? How do I add randomness to the algorithm?
  - How much randomness can I add without sacrificing efficiency?
  - How will I ensure that the algorithm isn't awfully slow?
  - How can I prevent infinite recursion and circular cases?

Each of these questions involved numerous design choices within themselves, but I'll focus on the more overaching design choice that helped provide a framework for answering all of these questions: my decision to use a greedy best-first-search inspired algorithm, while adding randomness. Greedy best first search uses a heuristic to recursively guide an algorithm to its destination. I knew that just randomly searching pathways would not cut it here, since there are so many possible pathways the packet could take, and testing all of them would be awfully slow. In fact, there is no real way to randomly test pathways, since my data representation of the routers did not include any connections between them (in real life, routers are connected, but in my program, they existed more as a sort of "unconnected graph"). So, I need some way to guide the algorithm, and I settled on three "heuristics" that greatly limit the number of options that the algorithm can choose from.
 
  1. The next point selected must be within a reasonable distance of the current point. The "neighbors" function filters the sample of routers that can be selected.
  2. Points that progress the algorithm closer to the destination are prioritized. I calculate this heuristic in a complex fashion, by creating a weighted random sample out of nearby points, in which routers closer to the destination are assigned a greater weight.
  3. If the routing algorithm encounters a landing point, it has the option to discard the previous two heuristics and send the packet overseas along the landing point's defined cable. It chooses to send the packet overseas only if it will send it to a continent not yet visited along the pathway.

At the same time, these heuristics only serve as loose guides. I wanted to maintain a degree of randomness in the algorithm along with the heuristics. Because of this, the algorithm is not a true greedy-best-first-search algorithm. Finding a balance between randomness and the "greediness" of greedy-BFS took a substantial amount of time, energy, tweaking, and profiling.

3. **Accumulators**: Accumulators, in particular, the "path" parameter that accumulates as the path is generated, were a huge help. They allowed me to monitor the state of the path as the algorithm progressed, and direct the algorithm based on certain conditions in the path.

4. **Maximum Cases**: Because of the breadth of points that the routing algorithms have to deal with, efficiency was a major consideration here. I was able to quicken the functions considerably by tweaking the algorithms and using a profile to track down what functions were taking the most time to execute. Nevertheless, I still came into hiccups with the algorithm. So, to prevent the algorithm from getting stuck, it not only deals with circular cases, but defines "maximum cases" that reinitialize the routing process if certain conditions are met. The two maximum cases are time-based (reroute if the current path is taking too much time) and length-based (reroute if the accumulated path is too long).


#### Takeaways

- **Benefits of unit testing**: I took some time to learn the basics of a Python testing library in order to test parts of my program. I certainly didn't test everything, because my program involves a lot of randomness (and testing unpredictable states is difficult), but testing certainly helped where it could.
- **Importance of diagraming**: Diagraming was the only way I could really visualize and understand the complex algorithms I was implementing.
- **Importance of version control**: I spend some time learning how to properly use Git such that I could isolate my development on a feature while keeping the main branch intact. This was super handy since I was constantly needing to scrap new features and revert code to previous states.
- **Project management**: I used Github's automated project boards and issues to manage all tasks relating to the project. This helped keep my head straight while implementing new features and fixing bugs. I can't emphasize enough the power of having a good project management system.
- **Perfection is the enemy of good**: To be completely honest, I spent way more time working on this project than I should have, oftentimes just trying to perfect a miniscule feature. More than anything else I've worked on in my life, this project taught me the importance of stepping back and assessing the true value of what you're working on. In many cases, the effort was not worth the result when working on this porject.
- **Mastery of fundamentals**: While I have a decent amount of programming experience now, this project showed me that I still have a long way to go, especially when it comes to fully understanding the fundamentals.
- **Importance of proper workspace setup**: I have never used Flask before, so properly setting up the project with packages, dependencies, configuration files, a virtual environment, and a testing library was a bit difficult for me, and I ran into many bumps because of it. Flask in particular is a very lightweight and customizable framework, so I had little guidance on the best way to organize my application. In the future, when learning a new framework, I will take more time to understand recommended file structure patterns and configurations.
- **Start simple**: The inital approach I took to this application was to develop it all at once, but I wish I had developed my program in multiple "drafts" (AKA versions), starting with a simpler interface and algorithms, and slowly adding complexity and randomness. This would have helped me avoid getting stuck countless times and running into countless regressions.
- **Using a debugger**: The debugger was my best friend. I didn't really use any integrated debugging tool when working on projects in the past, but developing this application without a debugger would have been painful.
- **Profiling**: A profiler was my other best friend. It helped me track down what functions were eating up most of the time in my code, so that I had an idea of where efficiency improvements were needed.
- **Be willing to use other people's code**: I found myself trying to reinvent the wheel multiple times in this application before using third-party packages and libraries. My philosophy was that I would try to do it myself first, and then get help if I needed it. While this is a helpful mindset for learning purposes, with such a large application, I would've been better off usng libraries first, and then trying to create my own implementations afterward, if I so desired. A great example of this was trying to implement a weighted-random-sampling function -- plenty of libraries exist that do this, but at first, I tried to create it myself.
