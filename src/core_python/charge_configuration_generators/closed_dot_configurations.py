from functools import partial
from itertools import product

import numpy as np


def sum_eq(array, sum):
    return np.sum(array) == sum


def closed_charge_configurations(n_continous, n_charge):
    floor_values = np.floor(n_continous).astype(int)
    n_dot = n_continous.size

    if floor_values.sum() > n_charge:
        return np.empty((0, n_dot))
    if (floor_values + 1).sum() < n_charge:
        return np.empty((0, n_dot))

    p = product([0, 1], repeat=floor_values.size)
    f = partial(sum_eq, sum=n_charge - floor_values.sum())
    combinations = filter(f, p)
    return np.stack(list(combinations), axis=0) + floor_values

