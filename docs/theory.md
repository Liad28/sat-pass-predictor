# Satellite Orbit Prediction: TLEs, SGP4, and Coordinate Transformations
Technical notes

## TLE Format
A Two-Line Element set (TLE) is a fixed-width text format used to distribute orbital data for Earth satellites. The two lines contain the parameters needed by the SGP4/SDP4 propagation model. A satellite name may appear on an additional line before the two-line element set.

The second line contains the main orbital parameters: inclination, eccentricity, right ascension of the ascending node (RAAN), argument of perigee, mean anomaly, and mean motion. The first line contains metadata such as the NORAD catalog number, international designator, epoch, mean-motion derivatives, the B* drag parameter, ephemeris type, element-set number, and checksum.

The elements in a TLE are not ordinary osculating Keplerian elements. They are mean elements fitted to observations for use with a particular propagation model, SGP4 (or its deep-space extension, SDP4). They should therefore be propagated with the model for which they were generated, rather than being treated as generic orbital elements and passed to an arbitrary propagator.

Mean motion, $n$, is given in revolutions per day. It is related to the semi-major axis, $a$, through the Keplerian relation below. This relation is useful for understanding the meaning of mean motion, but it does not replace SGP4 propagation.

$$
n = \sqrt{\frac{\mu}{a^3}} \qquad\Longrightarrow\qquad a = \left(\frac{\mu}{n^2}\right)^{1/3}
$$

For calculations in SI units, convert mean motion from revolutions per day to radians per second:

$$
n\ [\mathrm{rad/s}] = n\ [\mathrm{rev/day}]\times\frac{2\pi}{86{,}400}
$$

The TLE epoch specifies the reference time associated with the fitted elements. The age of the TLE is important because prediction quality generally degrades as the propagation time moves farther from the epoch.

## What SGP4 Includes and Neglects
SGP4 is a simplified analytical model designed for propagating Earth-satellite orbits from TLE data. Its perturbation terms are approximations chosen to work with the way TLE elements are generated.

### Effects represented in the model
* Earth’s zonal gravity harmonics, principally ${J}_{2}$, with additional ${J}_{3}$ and ${J}_{4}$ terms. These terms represent the part of Earth’s non-spherical gravitational field that is symmetric about the rotation axis. ${J}_{2}$ is the dominant contribution and produces secular precession of the RAAN and argument of perigee, as well as periodic orbital variations.  
* Atmospheric drag through the fitted B* parameter and a simplified atmospheric-density model. B* is a model parameter estimated as part of the TLE fit; it is not a direct measurement of atmospheric density and should not be interpreted as a standalone physical drag coefficient.  
* For deep-space objects, the SDP4 treatment includes lunar and solar gravitational perturbations and resonance terms relevant to certain orbital periods. The classical SGP4/SDP4 distinction uses an orbital period of approximately 225 minutes as the near-Earth/deep-space boundary. The deep-space treatment is particularly relevant to 12-hour Molniya-type and 24-hour geosynchronous resonances.

### Effects not fully represented
* Longitude-dependent (tesseral and sectoral) components of Earth’s gravity field are not treated in the same detailed way as in high-precision numerical orbit propagators.  
* Solar radiation pressure is not explicitly modelled as a general force in the standard near-Earth SGP4 treatment.  
* Relativistic effects and solid-Earth/ocean-tide effects are not included as high-precision corrections.  
* The atmosphere is represented through a simplified model. Real atmospheric density varies with solar activity, geomagnetic activity, local time, and other conditions; these variations are not dynamically resolved by the simple drag treatment.  
* Satellite manoeuvres, such as ISS reboosts or station-keeping burns, cannot be predicted unless their effects are reflected in subsequently updated orbital elements.

The fitted B* parameter can absorb some mismatch between the simplified model and the observations. This is one reason the TLE and SGP4/SDP4 should be treated as a coupled data-and-model system.

## Reference Frames and Coordinate Transformations
SGP4/SDP4 returns satellite position and velocity in the True Equator, Mean Equinox (TEME) reference frame. To calculate a satellite’s position relative to a ground observer, the state must be expressed in an Earth-fixed frame and then projected onto the observer’s local coordinate axes.

### TEME to an Earth-fixed frame
A practical transformation from TEME to an Earth-fixed frame such as ITRS/ITRF accounts for Earth rotation. In a simplified treatment, this is described as a rotation about the z-axis by the Greenwich Mean Sidereal Time (GMST). Because TEME uses the mean equinox, the equation of the equinoxes is not applied: the rotation angle is GMST, not GAST (Vallado et al., 2006). A more rigorous transformation also accounts for Earth-orientation parameters, including polar motion. Polar motion is often neglected in introductory or lower-accuracy applications, but it matters when higher positional accuracy is required.

In Skyfield, `EarthSatellite.at(t)` performs the TEME conversion internally and returns GCRS; topocentric alt/az is obtained with `(sat - station).at(t).altaz()`.

### Earth-fixed coordinates to the local ENU frame
Let the observer’s geodetic latitude, longitude, and height be $\phi$, $\lambda$, and $h$. The observer’s Earth-fixed position is $\mathbf r_s$, computed using the WGS84 reference ellipsoid. If the satellite Earth-fixed position is $\mathbf r_{\mathrm{sat}}$, the relative position vector from the observer to the satellite is:

$$
\boldsymbol{\rho}=\mathbf r_{\mathrm{sat}}-\mathbf r_s
$$

The local East-North-Up (ENU) unit vectors, expressed in Earth-fixed Cartesian coordinates, are:

$$
\mathbf E=(-\sin\lambda,\ \cos\lambda,\ 0)
$$

$$
\mathbf N=(-\sin\phi\cos\lambda,\ -\sin\phi\sin\lambda,\ \cos\phi)
$$

$$
\mathbf U=(\cos\phi\cos\lambda,\ \cos\phi\sin\lambda,\ \sin\phi)
$$

The elevation angle is obtained by projecting the relative vector onto the local Up direction:

$$
\mathrm{el}=\arcsin\left(\frac{\boldsymbol{\rho}\cdot\mathbf U}{|\boldsymbol{\rho}|}\right)
$$

The azimuth, measured clockwise from North, is:

$$
\mathrm{az}=\operatorname{atan2}(\boldsymbol{\rho}\cdot\mathbf E,\ \boldsymbol{\rho}\cdot\mathbf N)\ \bmod\ 360^\circ
$$

Here $\phi$ is the geodetic latitude, not the geocentric latitude. The local Up direction is normal to the WGS84 ellipsoid; it is not exactly the radial direction from Earth’s centre. The difference can reach approximately 0.19° at mid-latitudes.

These expressions give geometric elevation and azimuth. Atmospheric refraction is not included unless it is added separately, so the calculated elevation is not necessarily the apparent elevation seen by an observer.

## TLE Accuracy Over Time
TLE prediction accuracy depends on the quality and quantity of tracking observations, the orbit type, the space environment, and how well the SGP4/SDP4 model represents the satellite’s motion. Predictions generally become less reliable as the propagation time moves farther from the TLE epoch. This effect is particularly important for Low Earth Orbit (LEO) satellites, where atmospheric drag can change the orbit significantly.

For typical LEO objects, SGP4 position error is on the order of ~1 km at epoch and grows by roughly 1–3 km per day of propagation (Vallado et al., 2006). This project therefore warns when |TLE age| > 3 days (see `check_tle_age` in `tle.py`). This is an approximate engineering threshold, not a guaranteed accuracy bound: actual errors can be smaller or much larger depending on the satellite and conditions.

TLEs are updated as needed rather than on one universal fixed schedule. Frequently tracked or manoeuvring objects may receive updated elements more often than stable, low-drag objects. For pass prediction, the TLE epoch should therefore be checked and the newest suitable element set should be used.

### Why Drag Is the Dominant Source of Along-Track Error
Atmospheric drag removes orbital energy. For a near-circular orbit, this tends to decrease the semi-major axis $a$. Since mean motion depends on $a$ as $n\propto {a}^{-3/2}$, a decrease in $a$ causes the mean motion to increase.

$$
n\propto a^{-3/2}
$$

Differentiating the Keplerian relation gives:

$$
\dot n=-\frac{3}{2}\frac{n}{a}\dot a
$$

If the mean motion is approximated as changing at a constant rate over a limited interval, the angular orbital coordinate can be written as:

$$
u(t)\approx u_0+n_0t+\frac{1}{2}\dot n t^2
$$

An uncertainty in the rate of change of mean motion therefore produces an angular phase error that grows approximately quadratically with elapsed time. For a small phase error, the corresponding along-track displacement is approximately:

$$
\delta s\approx\frac{1}{2}a\,\delta\dot n\,t^2
$$

In this expression, $\delta \dot{n}$ is the uncertainty in the time derivative of mean motion, and the approximation assumes a small angular error and a roughly constant $\delta \dot{n}$ over the interval. Uncertainty in atmospheric density and in the fitted B* parameter contributes to uncertainty in the drag-induced evolution of the orbit.

In this simplified error picture, radial and cross-track errors are often smaller or more oscillatory, whereas along-track error tends to accumulate. This is not a universal rule for every orbit or every error source, but it explains why along-track error is often the main concern in short-term LEO pass prediction.

Cross-track error arises from errors in the orbital-plane orientation ($\delta i$, $\delta\Omega$) and appears as a once-per-revolution oscillation of amplitude $\sim a\,\delta i$; drag acts within the orbital plane and does not drive it secularly.

For a ground observer, an along-track position error appears mainly as a timing error: the satellite reaches a given point along its orbital path earlier or later than predicted. Consequently, even when the predicted ground track is broadly correct, the predicted rise, culmination, and set times can shift. For the ISS ($v\approx 7.66\ \mathrm{km/s}$), a 1 km along-track error corresponds to approximately 0.13 s in predicted pass times.

## References
* Hoots, F. R., & Roehrich, R. L. (1980). *Spacetrack Report No. 3: Models for Propagation of NORAD Element Sets*.  
* Vallado, D. A., Crawford, P., Hujsak, R., & Kelso, T. S. (2006). *Revisiting Spacetrack Report #3*. AIAA 2006-6753.  
* Skyfield documentation, *Earth Satellites*. [https://rhodesmill.org/skyfield/earth-satellites.html](https://rhodesmill.org/skyfield/earth-satellites.html)
