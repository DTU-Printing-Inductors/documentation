I could argue that with most of these CFI apporaches, they have a discrete inductance, aka how many materials with different permeabilities you have, that's what you get. But by tuning printing parameters you can get continous permeability or in other words you can get a gradient, I need to look into why and how can this discrete behaviour be beneficial.

I still kinda need the argument for why printing parameters over just geometrical or CAD differences, because in a way adjusting printing parameters are altering the geometry, and essentially were just making it harder to simulate by altering printing parameters and not geometry. Potentially, one difference would be that altering printing parameters could lead to smaller footprint, but I am not sure about the argument here. 

We can argue that multi material systems are more complex than a single material.

Researchers have explored different print setting, but they maybe haven't done different print settings in one print.

We can argue that altering the geometry is restricted by the printing resolution, so basically if we try to print a planar triangle, it will be discrete as the line width and line amount makes it blocky, yes there is arachne slicing engine to achieve dynamic extrusion line width, but maybe studying that also could be a gap. 

There still is no real argument to why altering printing parameters would be more advantageuos that chaning the geometry. Changing the printing parameters are changing the geometry.

This thought process lead to the hypothesis formation [[Print parameter varying multi-permeability]]

Another research gap would be continously doping while printing, so like a  extruder but it has two feeding channels, and we can adjust the magnetic particle loading on the fly, but then why not just do the geometry. This lead to [[]]