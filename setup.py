from setuptools import setup, Extension
import numpy as np
from distutils.command.build_ext import build_ext  # type: ignore

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
    Extension(
        'DLA.utils',
        [f'DLA/utils{ext}'],
        extra_compile_args=[]
    )
]

MSVC_FLAGS = ['/Ox']
REST_OF_COMPILERS_FLAGS = ['-O3', '--ffast-math']


class build_ext_compiler_check(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type

        flags = MSVC_FLAGS if 'msvc' in compiler else REST_OF_COMPILERS_FLAGS

        for extension in self.extensions:
            if extension in extensions:
                extension.extra_compile_args.extend(flags)


if USE_CYTHON:
    extensions = cythonize(extensions)

setup(
    name="DLA",
    ext_modules=extensions,
    include_dirs=[np.get_include()],
)
