## **TLE Format**

A Two-Line Element set (TLE) is a fixed-width format used to describe a satellite's orbit. It contains orbital parameters such as inclination, eccentricity, RAAN, argument of perigee, and mean anomaly, together with the satellite's mean motion and epoch. However, TLEs are not just a standard set of orbital elements: their values are fitted to observations using the SGP4/SDP4 propagation models. Therefore, they should be used with the model they were designed for, rather than treated as ordinary Keplerian elements.

## **What SGP4 Neglects**

SGP4 is a simplified propagation model designed to efficiently predict the motion of Earth-orbiting satellites. It does not describe every physical effect acting on a satellite with complete accuracy. Real orbits are affected by several perturbations, including atmospheric drag, Earth's non-spherical gravitational field, gravitational forces from other bodies, radiation pressure, and relativistic effects. The sources describe these as real orbital perturbations, but do not provide a complete list of which effects SGP4 specifically neglects. Its assumptions are also unsuitable for propagating the orbits of the Sun or Moon.

## **Reference Frames**

The SGP4/SDP4 model outputs satellite positions and velocities in the TEME (True Equator, Mean Equinox) reference frame. In this frame, the Z-axis points toward the instantaneous North Pole, while the X-axis is aligned with the mean direction of the vernal equinox. This is important because satellite coordinates must be interpreted in the correct reference frame before they can be compared with an observer's position on Earth.

## **TLE Accuracy Over Time**

The accuracy of a TLE depends on several factors, including the quality and quantity of tracking observations, the satellite's orbit, and changes in its environment. As time passes from the TLE epoch, predictions generally become less reliable, particularly for satellites in low Earth orbit, where atmospheric drag can significantly affect their motion. For a typical LEO satellite, SGP4 accuracy is approximately 1 km within a few days of the TLE epoch, although this is only a rough estimate and not a guarantee. TLEs are updated when needed rather than on a fixed schedule, so checking the age of the orbital data is essential when generating predictions.

