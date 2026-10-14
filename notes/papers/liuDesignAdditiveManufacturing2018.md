---
Title: Design and Additive Manufacturing of Multipermeability Magnetic Cores
Year: "2018"
Author: Lanbing Liu, Chao Ding, Shengchang Lu, Ting Ge, Yi Yan, Yunhui Mei, Khai D. T. Ngo, Guo-Quan Lu
Tags:
  - "#paper"
  - skimmed
URL: https://ieeexplore.ieee.org/document/8325522/
DOI: 10.1109/TIA.2018.2819963
Cite Key: "[@liuDesignAdditiveManufacturing2018]"
Entry: "[[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf]]"
---
## Source 

> [!PDF|yellow] [[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf#page=1&selection=120,44,123,48&color=yellow|Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores, p.1]]
> > Having uniform distribution of magnetic flux throughout an inductor core, the volume of the inductor can be reduced without sacrificing its inductance, leading to a higher power density and efficiency.


> [!PDF|yellow] [[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf#page=1&selection=139,15,141,25&color=yellow|Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores, p.1]]
> > These intricate configurations and geometries of cores and windings are difficult to fabricate, thus posing barriers for their implementation.
> 
> This is one of the papers main arguments 
## Interpretation
> [!PDF|red] [[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf#page=1&selection=110,0,114,48&color=red|Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores, p.1]]
> > AS MAGNETIC components typically take up a significant portion of size and weight of a power converter, innovations leading to compact designs of magnetic components can greatly improve power density of the system [1].
> 
> [[sullivanInvitedPassiveComponent2011]]

> [!PDF|red] [[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf#page=1&selection=120,43,125,22&color=red|Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores, p.1]]
> >  Having uniform distribution of magnetic flux throughout an inductor core, the volume of the inductor can be reduced without sacrificing its inductance, leading to a higher power density and efficiency. A further benefit of core volume reduction is the lower winding loss from reduced winding length
> 
> Having uniform distribution of magnetic flux throughout an inductor core, leads to the reduction in volume of the inductor without sacrificing its inductance. Furthermore, decreasing the core volume leads to lower winding loss due to reduced winding lenght. 
## Ideas
I could argue that with most of these CFI apporaches, they have a discrete inductance, aka how many materials with different permeabilities you have, that's what you get. But by tuning printing parameters you can get continous permeability or in other words you can get a gradient, I need to look into why and how can this discrete behaviour be beneficial.

I still kinda need the argument for why printing parameters over just geometrical or CAD differences, because in a way adjusting printing parameters are altering the geometry, and essentially were just making it harder to simulate by altering printing parameters and not geometry. Potentially, one difference would be that altering printing parameters could lead to smaller footprint, but I am not sure about the argument here. 

We can argue that multi material systems are more complex than a single material.

Researchers have explored different print setting, but they maybe haven't done different print settings in one print.

We can argue that altering the geometry is restricted by the printing resolution, so basically if we try to print a planar triangle, it will be discrete as the line width and line amount makes it blocky, yes there is arachne slicing engine to achieve dynamic extrusion line width, but maybe studying that also could be a gap. 

There still is no real argument to why altering printing parameters would be more advantageuos that chaning the geometry. Changing the printing parameters are changing the geometry.

This thought process lead to the hypothesis formation [[Print parameter varying multi-permeability]]

Another research gap would be continously doping while printing, so like a  extruder but it has two feeding channels, and we can adjust the magnetic particle loading on the fly, but then why not just do the geometry. This naturally lead to [[Functionally gradient material multi-permeability]]



> [!PDF|note] [[Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores.pdf#page=1&selection=126,0,129,20&color=note|Design_and_Additive_Manufacturing_of_Multipermeability_Magnetic_Cores, p.1]]
> > In order to reduce volume and increase power density of a magnetic component, several techniques have been reported [3]–[6] to improve the uniformity of magnetic flux distribution throughout the core.
> 
> Potentially this has been only explored in DIW + sintering setups. And exploring this concept in FDM might be new. And then we can potentially create the argument that altering print setting in these DIW + sintering setups don't matter in the end as it gets sintered, while polymer composited retain their original geometry. Need to investigate whether this has been done in FDM and does the argument stand.

## Connections
This work built upon the work in [[yanAdditiveManufacturingToroid2017]]
This work is part of the [[Virginia Tech, Department of Materials Science and Engineering]]
[[multi-permeability]]
## Summary
- What problem are the authors trying to solve?
    
- Why would multipermeability help?
    
- How did the authors implement it?
    
- What evidence shows that it worked?
    
- What limitations or unanswered questions remain?

See who cited the paper 
https://scholar.google.com/citations?view_op=view_citation&hl=en&user=NNuKERUAAAAJ&cstart=20&pagesize=80&sortby=pubdate&citation_for_view=NNuKERUAAAAJ:ufrVoPGSRksC