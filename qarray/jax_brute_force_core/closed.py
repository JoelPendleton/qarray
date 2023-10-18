"""
This module contains the functions for computing the ground state of a closed array, using jax.
"""
from functools import partial

import jax
import jax.numpy as jnp
from pydantic import NonNegativeInt

from .charge_configuration_generators import open_change_configurations_brute_force_jax
from ..qarray_types import VectorList, CddInv, Cgd_holes, Cdd


def ground_state_closed_jax_brute_force(vg: VectorList, cgd: Cgd_holes, cdd: Cdd, cdd_inv: CddInv,
                                        n_charge: NonNegativeInt) -> VectorList:
    """
   A jax implementation for the ground state function that takes in numpy arrays and returns numpy arrays.
    :param vg: the dot voltage coordinate vectors to evaluate the ground state at
    :param cgd: the dot to dot capacitance matrix
    :param cdd: the dot to dot capacitance matrix
    :param cdd_inv: the inverse of the dot to dot capacitance matrix
    :param n_charge: the total number of charge carriers in the array
    :return: the lowest energy charge configuration for each dot voltage coordinate vector
   """

    n_list = open_change_configurations_brute_force_jax(n_dot=cdd.shape[0], n_max=n_charge)
    f = partial(_ground_state_closed_0d, cgd=cgd, cdd_inv=cdd_inv, n_charge=n_charge, n_list=n_list)

    match jax.local_device_count():
        case 0:
            raise ValueError('Must have at least one device')
        case _:
            f = jax.vmap(f)
    return f(vg)


@jax.jit
def _ground_state_closed_0d(vg: jnp.ndarray, cgd: jnp.ndarray, cdd_inv: jnp.ndarray,
                            n_charge: NonNegativeInt, n_list, T=0.0) -> jnp.ndarray:
    """
    Computes the ground state for a closed array.
    :param vg: the dot voltage coordinate vector
    :param cgd: the dot to dot capacitance matrix
    :param cdd_inv: the inverse of the dot to dot capacitance matrix
    :param cdd: the dot to dot capacitance matrix
    :param n_charge: the total number of charge carriers in the array
    :return: the lowest energy charge configuration
    """

    mask = (jnp.sum(n_list, axis=-1) != n_charge) * jnp.inf
    v_dash = cgd @ vg
    # computing the free energy of the change configurations
    F = jnp.einsum('...i, ij, ...j', n_list - v_dash, cdd_inv, n_list - v_dash)
    F = F + mask

    def softargmin():
        weights = jax.nn.softmax(-F / T, axis=0)
        return (n_list * weights[:, None]).sum(axis=0)

    def hardargmin():
        return n_list[jnp.argmin(F)]

    return jax.lax.cond(T > 0., softargmin, hardargmin)
