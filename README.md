# Clark's Conan, CMake, C++ Project Tools

This project started out as a collection of small scripts to automate the configure, build, and testing steps of
C++ projects I work on. It has since grown to include several small utilities that I have found useful while
working on C++ projects.


## Overview

While CMake has its issues, and there are many that despise it, it is the de facto standard for building C++ projects.
Most people's objections with CMake have to do with its home-grown scripting language. The command line interface
is actually quite nice. Not only does it support multiple generators, but it abstracts away many of the differences
between the generated build systems. For example, on Linux, you might do something like this:

```
$ mkdir build
$ cd build
$ cmake ..
$ make
```

But on Windows you might do:
```
$ mkdir build
$ cd build
$ cmake ..
$ msbuild MyProject.vcxproj
```

But with the `cmake --build` tool, you can do
```
$ mkdir build
$ cd build
$ cmake ..
$ cmake --build .
```
This works for Makefiles, Visual Studio Solutions, Ninja, etc.
What's more, if you follow the normal conventions, these four lines should
build any CMake project you create (things get more complicated if you need to
support custom options, but you should still have a default build that will just work).

I found that I was constantly running these commands, so I just put them into a script and eventually that morphed into
`ccc`. I also do most of my development on Linux, but occasionally need to build projects on Windows (mostly for testing),
so I wanted something I could run on either platform and have it "just work".

## Usage

### Installing

You can install `ccc` with pip.

```
$ pip install conan-cmake-cpp-project-tools
```

This may be an out-of-date version. To use the latest version, clone this repository and install with pip
```
$ cd cccpt
$ pip install .
```

### Requirements

`ccc` expects several standard tools to be installed. It makes use of these tools wherever possible, rather
than re-implementing functionality. Current dependencies are:

- Python (required)
- CMake (required)
- git (required)
- Conan (optional)

If you don't use these tools, then `ccc` won't be useful.

### Commands

To build a C++ project, run
```
$ ccc build
```
from anywhere in the project directory.
This will create a build directory in the project root
(`git` is used to find the project root), install any dependencies specified in a `conanfile.txt` file,
and configure and build (by default, Debug mode is built) the project.

To run the unit tests
```
$ ccc test
```
This will automatically run the build step, so it possible to run this command on a fresh copy of the project.
Currently this command just looks for executables created in the build directory that match file name patterns
I commonly use, so it may not work for you.

To build or test in Release mode, pass either command the `-R` option.

To get a list of all source files in the project
```
$ ccc list-sources
```
This is useful for triggering the unit tests to run when a file changes with the `entr` command.
```
$ ccc list-sources | entr ccc test
```

To install a project into a given root directory
```
$ ccc install /path/to/install/dir
```
This will run `CMake` with the `-DCMAKE_INSTALL_PREFIX=/path/to/install/dir` option, build the project in release mode,
and then run `cmake --build . --target install`.

There are many other commands that I find useful in my developement workflow. You may or may not find them useful. To get
a list of all commands, run
```
$ ccc --help
```
