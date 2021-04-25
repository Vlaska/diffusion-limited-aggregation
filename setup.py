from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name="utils",
    ext_modules=cythonize("DLA/utils.pyx"),
    # zip_safe=False,
    include_dirs=[np.get_include()],
    # package_dir = {"": "DLA"}
)
