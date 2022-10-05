import io
import os
import subprocess
import sys


from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
import sysconfig
import itertools


def get_python_library(python_version):
    """Get path to the python library associated with the current python
    interpreter."""
    # determine direct path to libpython
    python_library = sysconfig.get_config_var("LIBRARY")

    # if static (or nonexistent), try to find a suitable dynamic libpython
    if python_library is None or os.path.splitext(python_library)[1][-2:] == ".a":

        candidate_lib_prefixes = ["", "lib"]

        candidate_extensions = [".lib", ".so", ".a"]
        if sysconfig.get_config_var("WITH_DYLD"):
            candidate_extensions.insert(0, ".dylib")

        candidate_versions = [python_version]
        if python_version:
            candidate_versions.append("")
            candidate_versions.insert(0, "".join(python_version.split(".")[:2]))

        abiflags = getattr(sys, "abiflags", "")
        candidate_abiflags = [abiflags]
        if abiflags:
            candidate_abiflags.append("")

        # Ensure the value injected by virtualenv is
        # returned on windows.
        # Because calling `sysconfig.get_config_var('multiarchsubdir')`
        # returns an empty string on Linux, `du_sysconfig` is only used to
        # get the value of `LIBDIR`.
        libdir = sysconfig.get_config_var("LIBDIR")
        if sysconfig.get_config_var("MULTIARCH"):
            masd = sysconfig.get_config_var("multiarchsubdir")
            if masd:
                if masd.startswith(os.sep):
                    masd = masd[len(os.sep) :]
                libdir = os.path.join(libdir, masd)

        if libdir is None:
            libdir = os.path.abspath(
                os.path.join(sysconfig.get_config_var("LIBDEST"), "..", "libs")
            )

        candidates = (
            os.path.join(libdir, "".join((pre, "python", ver, abi, ext)))
            for (pre, ext, ver, abi) in itertools.product(
                candidate_lib_prefixes,
                candidate_extensions,
                candidate_versions,
                candidate_abiflags,
            )
        )

        for candidate in candidates:
            if os.path.exists(candidate):
                # we found a (likely alternate) libpython
                python_library = candidate
                break

    # TODO(opadron): what happens if we don't find a libpython?

    return python_library


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        extdir = os.path.join(extdir, "pasteboard")

        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cfg = "Debug" if self.debug else "Release"

        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}".format(extdir),
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={}".format(extdir),
            "-DPYTHON_EXECUTABLE={}".format(sys.executable),
            "-DPYTHON_INCLUDE_DIR={}".format(sysconfig.get_path("include")),
            "-DPYTHON_LIBRARY={}".format(
                get_python_library(sysconfig.get_python_version())
            ),
            "-DCMAKE_BUILD_TYPE={}".format(cfg),
            "-DCMAKE_CROSSCOMPILING=ON",
            "-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64",
            "-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0",
        ]

        build_args = []

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += ["-j{}".format(self.parallel)]
            else:
                build_args += ["-j4"]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )


if sys.version_info < (3, 0):
    sys.exit("Sorry, Python < 3.0 is not supported")

requirements = ["numpy", "tqdm", "requests", "portalocker", "opencv-python"]

with io.open("README.md", encoding="utf-8") as h:
    long_description = h.read()

setup(
    name="pasteboard",
    version="2022.10.4",
    author="Toby Fleming",
    author_email="tobywf@users.noreply.github.com",
    description="Pasteboard - Python interface for reading from NSPasteboard (macOS clipboard)",
    url="https://github.com/tobywf/pasteboard",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X :: Cocoa",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Objective C",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Desktop Environment",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=["macOS", "clipboard", "pasteboard"],
    license="MPL-2.0",
    python_requires=">=3.5",
    packages=find_packages("src/pasteboard"),
    package_dir={"": "src/pasteboard"},
    install_requires=requirements,
    ext_modules=[CMakeExtension("pasteboard")],
    cmdclass={"build_ext": CMakeBuild},
)
