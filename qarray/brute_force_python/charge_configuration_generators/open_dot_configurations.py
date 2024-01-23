"""
This module contains the functions for computing the ground state of an open array.
"""

import numpy as np


def open_change_configurations_brute_force_python(n_dot, n_max):
    """
    Generates all possible charge configurations for an open array.
    :param n_continuous:
    :return: a tensor of shape (n_max ** n_dot, n_dot) containing all possible charge configurations
    """

    args = np.zeros((n_dot, n_max + 1)) + np.arange(0, n_max + 1)
    number_of_configurations = (n_max + 1) ** n_dot
    configurations = np.stack(np.meshgrid(*args), axis=-1).reshape(number_of_configurations, n_dot)
    return configurations
