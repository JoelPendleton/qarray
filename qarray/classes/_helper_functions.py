import numpy as np
from pydantic import NonNegativeInt

from ..brute_force import ground_state_open_brute_force, ground_state_closed_brute_force
from ..jax_core import ground_state_open_jax, ground_state_closed_jax
from ..python_core import ground_state_open_python, ground_state_closed_python
from ..qarray_types import VectorList
from ..rust_core import ground_state_open_rust, ground_state_closed_rust


def _validate_vg(vg: VectorList, n_gate: NonNegativeInt):
    """
    This function is used to validate the shape of the dot voltage array.
    :param vg: the dot voltage array
    """
    if vg.shape[-1] != n_gate:
        raise ValueError(f'The shape of vg is in correct it should be of shape (..., n_gate) = (...,{n_gate})')


def _ground_state_open(model, vg: VectorList | np.ndarray) -> np.ndarray:
    """
    This function is used to compute the ground state for an open system.
    :param vg: the dot voltages to compute the ground state at
    :return: the lowest energy charge configuration for each dot voltage coordinate vector
    """

    # validate the shape of the dot voltage array
    _validate_vg(vg, model.n_gate)

    # grabbing the shape of the dot voltage array
    vg_shape = vg.shape
    nd_shape = (*vg_shape[:-1], model.n_dot)
    # reshaping the dot voltage array to be of shape (n_points, n_gate)
    vg = vg.reshape(-1, model.n_gate)

    # performing the type conversion if necessary
    if not isinstance(vg, VectorList):
        vg = VectorList(vg)

    # calling the appropriate core function to compute the ground state
    match model.core:
        case 'rust' | 'Rust' | 'RUST' | 'r':
            result = ground_state_open_rust(
                vg=vg, cgd=model.cgd,
                cdd_inv=model.cdd_inv,
                threshold=model.threshold,
                polish=model.polish, T=model.T
            )
        case 'jax' | 'Jax' | 'JAX' | 'j':
            if model.threshold < 1.:
                print('Warning: JAX core does not support threshold < 1.0, using threshold of 1.0')

            result = ground_state_open_jax(
                vg=vg, cgd=model.cgd,
                cdd_inv=model.cdd_inv, T=model.T
            )

        case 'brute_force' | 'jax_brute_force' | 'Jax_brute_force' | 'JAX_BRUTE_FORCE' | 'b':

            if model.max_charge_carriers is None:
                message = ('The max_charge_carriers must be specified for the jax_brute_force core use:'
                           '\nmodel.max_charge_carriers = #')
                raise ValueError(message)

            if model.threshold < 1.:
                print('Warning: JAX core does not support threshold < 1.0, using threshold of 1.0')
            result = ground_state_open_brute_force(
                vg=vg, cgd=model.cgd,
                cdd_inv=model.cdd_inv, max_number_of_charge_carriers=model.max_charge_carriers, T=model.T
            )
        case 'python' | 'Python' | 'PYTHON' | 'p':
            result = ground_state_open_python(
                vg=vg, cgd=model.cgd,
                cdd_inv=model.cdd_inv,
                threshold=model.threshold,
                polish=model.polish
            )
        case _:
            raise ValueError(f'Incorrect core {model.core}, it must be either rust, jax or python')
    assert np.all(result.astype(int) >= 0), 'The number of charges is negative something went wrong'
    return result.reshape(nd_shape)


def _ground_state_closed(model, vg: VectorList | np.ndarray, n_charge: NonNegativeInt) -> np.ndarray:
    """
    This function is used to compute the ground state for a closed system, with a given number of changes.
    :param vg: the dot voltages to compute the ground state at
    :param n_charge: the number of changes in the system
    :return: the lowest energy charge configuration for each dot voltage coordinate vector
    """
    # validate the shape of the dot voltage array
    _validate_vg(vg, model.n_gate)

    # grabbing the shape of the dot voltage array
    vg_shape = vg.shape
    nd_shape = (*vg_shape[:-1], model.n_dot)
    # reshaping the dot voltage array to be of shape (n_points, n_gate)
    vg = vg.reshape(-1, model.n_gate)

    # performing the type conversion if necessary
    if not isinstance(vg, VectorList):
        vg = VectorList(vg)

    # calling the appropriate core function to compute the ground state
    match model.core:
        case 'rust' | 'Rust' | 'RUST' | 'r':
            result = ground_state_closed_rust(
                vg=vg, n_charge=n_charge, cgd=model.cgd,
                cdd=model.cdd, cdd_inv=model.cdd_inv,
                threshold=model.threshold, polish=model.polish, T=model.T
            )

        case 'jax' | 'Jax' | 'JAX' | 'j':
            if model.threshold < 1.:
                print('Warning: JAX core does not support threshold < 1.0, using of 1.0')
            result = ground_state_closed_jax(
                vg=vg, n_charge=n_charge, cgd=model.cgd,
                cdd=model.cdd, cdd_inv=model.cdd_inv, T=model.T
            )

        case 'brute_force' | 'jax_brute_force' | 'Jax_brute_force' | 'JAX_BRUTE_FORCE' | 'b':
            if model.threshold < 1.:
                print('Warning: JAX core does not support threshold < 1.0, using threshold of 1.0')

            result = ground_state_closed_brute_force(
                vg=vg, n_charge=n_charge, cgd=model.cgd,
                cdd=model.cdd, cdd_inv=model.cdd_inv, T=model.T
            )

        case 'python' | 'Python' | 'PYTHON' | 'p':
            result = ground_state_closed_python(
                vg=vg, n_charge=n_charge, cgd=model.cgd,
                cdd=model.cdd, cdd_inv=model.cdd_inv,
                threshold=model.threshold, polish=model.polish
            )
        case _:
            raise ValueError(f'Incorrect core {model.core}, it must be either rust, jax or python')

    assert np.all(
        np.isclose(result.sum(axis=-1), n_charge)), 'The number of charges is not correct something went wrong'

    return result.reshape(nd_shape)
