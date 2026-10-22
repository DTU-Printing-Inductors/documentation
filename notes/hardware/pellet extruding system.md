## Hotend
Custom
https://link.springer.com/article/10.1007/s40964-024-00926-0

I ignored large extruders.

| Extruder             | Type     | Price    | Nozzle                     | Screw type  | Notes                                               | Link                                                                                                           |
| -------------------- | -------- | -------- | -------------------------- | ----------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Mahor V4             | Extruder | 6000 dkk | V6                         | Compression | Jorge Canada and others academically have used this | https://mahor.xyz/producto/v4-pellet-extruder/                                                                 |
| Mahor V5 PRO         | Extruder | 9000 dkk | V6                         | Compression | New design, 360 ceramic heating, hardened steel     | https://filament2print.com/en/extruders/3089-19279-pellet-extruder-mahor-v5-m8.html#/2542-version-professional |
| LILY Pellet Extruder | Extruder | 6400 dkk | Potentially propietary     | Compression | Looks like brass construction                       | https://shop.recycl3dprint.com/products/lily-pellet-extruder-assembled                                         |
| TUMAKER MINI MODULAR | Printer  | n/a      | n/a                        | n/a         | Looks like the mahor v4 clone                       | https://tumaker.com/tumaker-mini-modular-pellet-filament-2                                                     |
| Ginger Additive G1   | Extruder | 53k dkk  | Proprietary (1.8/3/5/8 mm) | n/a         | Too large, and out of stock                         | https://www.gingeradditive.com/products/g1-extruder?variant=55840795361628                                     |
| Direct3D extruder    | Extruder | quote    | Vulcano V6 (if i remember) | Compression | Not a lot of info                                   | https://www.direct3d.it/extruders/                                                                             |
| Wasp HDP             | Extruder | quote    | V6                         | n/a         |                                                     | https://www.3dwasp.com/en/robot-pellet-extruder-hdp/                                                           |
| Dyze Pulsar Atom     | Extruder | quote    | Proprietary                | n/a         |                                                     | https://dyzedesign.com/pulsar-atom-pellet-extruder/                                                            |
A review paper choses Mahor, see [[shaikScientificReviewVarious2021]]

## If the blend ratios do not work
What I can do is take two pellet extruders and combine them, and have them coextrude, similar how the filament extruders do it, and then i can design a mixer inside the heater block for them to mix. This solution is good, in the case where pellet feeding might be hard to achieve with the specific ratios, controlling steppers is easier. There is another case, where two hoppers might exist, that are controlled with stepper motors to precisely dose, but then we have 3 steppers, instead of the two

Another approach could be using direct powder extrusion.
## Pellet feeding
For now I don't think about this until the blend ratios are proven.

## Connections
[[Soft magnetic pellets]]
