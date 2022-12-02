cmake_minimum_required(VERSION 3.16)

project(ConanCMakeProject)

find_package(Boost REQUIRED)

add_library(libA src/libA.cpp)
target_include_directories(libA PUBLIC src)
target_link_libraries( libA Boost::boost )

add_subdirectory(testing)
