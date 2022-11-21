cmake_minimum_required(VERSION 3.16)

add_executable(unitTests main.cpp libA_tests.cpp)

target_link_libraries(unitTests libA)
