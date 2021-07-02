from platform import system
from setuptools import setup, Extension, find_packages
import numpy as np

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

ext = '.pyx' if USE_CYTHON else '.c'

MSVC_FLAGS = ['/Ox']
REST_OF_COMPILERS_FLAGS = ['-O3', '-ffast-math']

extensions = [
    Extension(
        'DLA.utils',
        [f'DLA/utils{ext}'],
        extra_compile_args=(
            MSVC_FLAGS if system() == 'Windows' else REST_OF_COMPILERS_FLAGS
        )
    )
]


if USE_CYTHON:
    extensions = cythonize(extensions)

setup(
    name='DLA',
    version='1.1.2',
    ext_modules=extensions,
    package_dir={'': '.'},
    packages=find_packages(where='.'),
    include_dirs=[np.get_include()],
    package_data={
        '': ['*.yml'],
        '**': ['*.yml'],
    },
    extras_require={
        'display': ["pygame >= 2.0.1"],
    },
    install_requires=[
        "numpy>=1.20.2",
        "PyYAML>=5.4.1",
        "beautifultable>=1.0.1",
        "click>=8.0.1",
        "loguru>=0.5.3",
    ]
)
