import os
from copy import deepcopy

def extend_path(lop):
    env = os.environ.copy()
    new_path = ':'.join(lop)
    new_path = new_path + ":" if lop else new_path
    new_path += env['PATH']
    env['PATH'] = new_path
    return env


def add_env_vars(source_env, extension_vars):
    new_env = deepcopy(source_env)
    for var, val in extension_vars.items():
        new_env[var] = val
    return new_env
