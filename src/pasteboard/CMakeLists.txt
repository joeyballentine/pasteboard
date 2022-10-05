cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

project(pasteboard LANGUAGES CXX OBJC)

add_library(pasteboard SHARED pasteboard.m)

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(pasteboard ${PYTHON_LIBRARIES})