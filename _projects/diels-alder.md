---
title: Computational description of Diels-Alder reactions 
description: Reproducing some published DFT calculations
date: 2025-12-19
---
The reaction between acrylonitrile and cyclopentadiene (reaction B1 in Loco et. al.) was selected as a sort of proof-of-concept that my setup was actually capable of running the relevant computations. One of the combinations benchmarked and recommended by the paper is the ωB97XD functional with a 6-31G basis set because it's cheap and accurate. I used the ωB97X with D3BJ dispersion instead (yes, they are different methods...) with the same basis set because ORCA doesn't provide the ωB97XD functional.

A relaxed surface scan was conducted first in order to find an initial structure close enough to the transition state. This ran for 13 hours because I forgot about it and turned off my laptop at some point before it finished; had I not done that I expect it would have taken around 2 hours. I had Claude plot the energy against the scanned coordinate to identify the structure most similar to the transition state.

![Relaxed surface scan for the reaction between cyclopentadiene and acrylonitrile](/assets/images/relaxscan_blog.png)

The Avogadro file corresponding to the maximum energy configuration was used for a transition state optimisation, which completed in around 13 minutes. Both of my previous transition state searches hit the maximum number of optimisation cycles around an hour in, so I was fairly confident I had the correct transition state. In order to verify this, I ran a frequency calculation -- transition states must have exactly one imaginary vibrational frequency. It was not immediately obvious to me why this was the case. In essence, on a potential energy surface (or PES, a plot of energy against $ 3N-6 $ nuclear coordinates), transition states are saddle points lying between two local minima. Analogous to how local minima are critical points with no negative second derivatives, transition states are critical points with exactly one negative second derivative. The connection between this and the frequency analysis is that chemical bonds, like springs, have specific ways in which they can vibrate, and they do so at specific frequencies 

$$ v \propto \sqrt{\frac{k}{m}}. $$

Just as with classical springs, $ k $ is simply the second derivative of energy with respect to (nuclear) position, and therefore the vibrational frequency for exactly one vibrational mode will be the square root of a negative number -- an imaginary frequency. The results of the frequency calculation are shown below (note that ORCA uses the negative sign (-) for imaginary numbers).

| Mode | Frequency (cm⁻¹) | Note |
|---------|------------------------|------|
| 4 | 0.00 | |
| 5 | 0.00 | |
| 6 | -543.33 | imaginary mode |
| 7 | 93.21 | |
| 8 | 136.37 | |
| 9 | 260.99 | |
| 10 | 279.50 | |

We have our transition state. pretty neat.

Failure log
B1 - acrylonitrile with cyclopentadiene

Transition state optimisation run 1: Maximum cycles reached, result was product-like

Relaxed surface scan run 1: Unclear what went wrong but energy at 1.8A should not be higher than the transition state. Also energy barrier is much larger than reported by Loco et. al.
![](/assets/images/relaxscan-B1-bad.png)

Transition state optimisation run 2 - Didn't use the result from the relaxed surface scan, but initial structure was poorly drawn. Maximum cycles reached, terminated at an aziridine.
![](/assets/images/bad-optTS.jpg)

Relaxed surface scan run 2 (2D): Same as previous surface scan, energy barrier is more reasonable but still much larger than expected.
![](/assets/images/relaxscan-B1-2D.png)

1. Loco, D., Chataigner, I., Piquemal, J.-P., & Spezia, R. (2022). Efficient and Accurate Description of Diels-Alder Reactions Using Density Functional Theory. ChemPhysChem, 23(18), e202200349. https://doi.org/10.1002/cphc.202200349