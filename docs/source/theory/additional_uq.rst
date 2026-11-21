Additional Uncertainty Quantification
=====================================

The nuclear data-induced uncertainties calculated as part of WINDIGO's 
post-processing will carry their own forms of uncertainty. These include Monte Carlo
stochastic uncertainty due to the usage of OpenMC to calculate the nuclear data 
uncertainties, and finite sampling uncertainty associated with the stochastic sampling 
method. This section covers the theory underlying the propagation of these additional 
uncertainties attached to the nuclear data-induced uncertainties computed using the direct
perturbation and stochastic sampling methods.