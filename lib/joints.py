"""
Methods for calculating joint parameters, such as joint centers and axes.

GNU GPL v3.0
Lukas Adamowicz

V0.1 - March 8, 2019
"""
from numpy import array, zeros, logical_and, abs as nabs, concatenate, cross
from numpy.linalg import lstsq, norm
from scipy.optimize import least_squares


class Center:
    def __init__(self, g=9.81, method='SAC', mask_input=True, min_samples=1000, opt_kwargs={}):
        """
        Object for joint center computation

        Parameters
        ----------
        g : float, optional
            Local value of gravitational acceleration. Default is 9.81 m/s^2.
        method : {'SAC', 'SSFC', 'SSFCv'}, optional
            Method to use for the computation of the joint center. Default is SAC. See Crabolu et al. for more details.
            SSFCv is SSFC but using vectors instead of magnitude, which requires rotations between sensors.
        mask_input : bool, optional
            Mask the input to only use the highest acceleration samples. Default is True
        min_samples : int, optional
            Minimum number of samples to use. Default is 1000.
        opt_kwargs : dict, optional
            Optimization key-word arguments. SAC uses numpy.linalg.lstsq.
            SSFC and SSFCv use scipy.optimize.least_squares.

        References
        ----------
        Crabolu et al. In vivo estimation of the shoulder joint center of rotation using magneto-inertial sensors:
        MRI-based accuracy and repeatability assessment. BioMedical Engineering Online. 2017.
        """
        self.g = g
        self.method = method
        self.mask_input = mask_input
        self.min_samples = min_samples
        self.opt_kwargs = opt_kwargs

    def compute(self, prox_a, dist_a, prox_w, dist_w, prox_wd, dist_wd, R_dist_prox):
        """
        Perform the computation of the joint center to sensor vectors.

        Parameters
        ----------
        prox_a : numpy.ndarray
            Nx3 array of accelerations measured by the joint proximal sensor.
        dist_a : numpy.ndarray
            Nx3 array of accelerations measured by the joint distal sensor.
        prox_w : numpy.ndarray
            Nx3 array of angular velocities measured by the joint proximal sensor.
        dist_w : numpy.ndarray
            Nx3 array of angular velocities measured by the joint distal sensor.
        prox_wd : numpy.ndarray
            Nx3 array of angular accelerations measured by the joint proximal sensor.
        dist_wd : numpy.ndarray
            Nx3 array of angular accelerations measured by the joint distal sensor.
        R_dist_prox : numpy.ndarray
            Nx3x3 array of rotations from the distal sensor frame to the proximal sensor frame.

        Returns
        -------
        prox_r : numpy.ndarray
            Joint center to proximal sensor vector.
        dist_r : numpy.ndarray
            Joint center to distal sensor vector.
        residual : float
            Residual value per sample used from the joint center optimization
        """
        if self.method == 'SAC':
            if self.mask_input:
                prox_an = norm(prox_a, axis=1) - self.g
                dist_an = norm(dist_a, axis=1) - self.g

                mask = zeros(prox_an.shape, dtype=bool)
                thresh = 0.8
                while mask.sum() < self.min_samples:
                    mask = logical_and(nabs(prox_an) > thresh, nabs(dist_an) > thresh)

                    thresh -= 0.05
                    if thresh < 0.09:
                        raise ValueError('Not enough samples or samples with high motion in the trial provided.  '
                                         'Use another trial')
            else:
                mask = zeros(prox_a.shape[0], dtype=bool)
                mask[:] = True

            # create the skew symmetric matrix products
            prox_K = array([[-prox_w[mask, 1] ** 2 - prox_w[mask, 2] ** 2,
                             prox_w[mask, 0] * prox_w[mask, 1] - prox_wd[mask, 2],
                             prox_wd[mask, 1] + prox_w[mask, 0] * prox_w[mask, 2]],
                            [prox_wd[mask, 2] + prox_w[mask, 0] * prox_w[mask, 1],
                             -prox_w[mask, 0] ** 2 - prox_w[mask, 2] ** 2,
                             prox_w[mask, 1] * prox_w[mask, 2] - prox_wd[mask, 0]],
                            [prox_w[mask, 0] * prox_w[mask, 2] - prox_wd[mask, 1],
                             prox_wd[mask, 0] + prox_w[mask, 1] * prox_w[mask, 2],
                             -prox_w[mask, 0] ** 2 - prox_w[mask, 1] ** 2]]).transpose([2, 0, 1])

            dist_K = array([[-dist_w[mask, 1] ** 2 - dist_w[mask, 2] ** 2,
                             dist_w[mask, 0] * dist_w[mask, 1] - dist_wd[mask, 2],
                             dist_wd[mask, 1] + dist_w[mask, 0] * dist_w[mask, 2]],
                            [dist_wd[mask, 2] + dist_w[mask, 0] * dist_w[mask, 1],
                             -dist_w[mask, 0] ** 2 - dist_w[mask, 2] ** 2,
                             dist_w[mask, 1] * dist_w[mask, 2] - dist_wd[mask, 0]],
                            [dist_w[mask, 0] * dist_w[mask, 2] - dist_wd[mask, 1],
                             dist_wd[mask, 0] + dist_w[mask, 1] * dist_w[mask, 2],
                             -dist_w[mask, 0] ** 2 - dist_w[mask, 1] ** 2]]).transpose([2, 0, 1])

            # create the oversized A and b matrices
            A = concatenate((prox_K, -R_dist_prox[mask] @ dist_K), axis=2).reshape((-1, 6))
            b = (prox_a[mask].reshape((-1, 3, 1))
                 - R_dist_prox[mask] @ dist_a[mask].reshape((-1, 3, 1))).reshape((-1, 1))

            # solve the linear least squares problem
            r, residual, _, _ = lstsq(A, b, rcond=None)
            r.resize((6,))
            residual = residual[0]

        elif self.method == 'SSFC':
            r_init = zeros((6,))

            if self.mask_input:
                prox_an = norm(prox_a, axis=1) - self.g
                dist_an = norm(dist_a, axis=1) - self.g

                mask = zeros(prox_an.shape, dtype=bool)
                thresh = 0.8
                while mask.sum() < self.min_samples:
                    mask = logical_and(nabs(prox_an) > thresh, nabs(dist_an) > thresh)

                    thresh -= 0.05
                    if thresh < 0.09:
                        raise ValueError('Not enough samples or samples with high motion in the trial provided.  '
                                         'Use another trial')
            else:
                mask = zeros(prox_a.shape[0], dtype=bool)
                mask[:] = True

            # create the arguments to be passed to both the residual and jacobian calculation functions
            args = (prox_a[mask], dist_a[mask], prox_w[mask], dist_w[mask], prox_wd[mask], dist_wd[mask])

            sol = least_squares(Center.compute_distance_residuals, r_init.flatten(), args=args, **self.opt_kwargs)
            r = sol.x
            residual = sol.cost

        return r[:3], r[3:], residual / mask.sum()

    @staticmethod
    def compute_distance_residuals(r, a1, a2, w1, w2, wd1, wd2):
        """
            Compute the residuals for the given joint center locations for proximal and distal inertial data

            Parameters
            ----------
            r : numpy.ndarray
                6x1 array of joint center locations.  First three values are proximal location guess, last three values
                are distal location guess.
            a1 : numpy.ndarray
                Nx3 array of accelerations from the proximal sensor.
            a2 : numpy.ndarray
                Nx3 array of accelerations from the distal sensor.
            w1 : numpy.ndarray
                Nx3 array of angular velocities from the proximal sensor.
            w2 : numpy.ndarray
                Nx3 array of angular velocities from the distal sensor.
            wd1 : numpy.ndarray
                Nx3 array of angular accelerations from the proximal sensor.
            wd2 : numpy.ndarray
                Nx3 array of angular accelerations from the distal sensor.

            Returns
            -------
            e : numpy.ndarray
                Nx1 array of residuals for the given joint center location guess.
            """
        r1 = r[:3]
        r2 = r[3:]

        at1 = a1 - cross(w1, cross(w1, r1, axisb=0)) - cross(wd1, r1, axisb=0)
        at2 = a2 - cross(w2, cross(w2, r2, axisb=0)) - cross(wd2, r2, axisb=0)

        return norm(at1, axis=1) - norm(at2, axis=1)

