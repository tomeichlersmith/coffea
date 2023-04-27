"""Tools to interface with various ML inference services

Providing the interfaces to the run ML inference such that user can simply
handle data mangling in awkward/numpy formats. Specifics of passing numpy arrays
conversion and the handling of dask are mostly abstract away.
"""
from .helper import numpy_call_wrapper
from .triton_wrapper import triton_wrapper
from .torch_wrapper import torch_wrapper

__all__ = [
    "numpy_call_wrapper",
    "triton_wrapper",
    "torch_wrapper",
]
