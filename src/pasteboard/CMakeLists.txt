cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

project(pasteboard LANGUAGES CXX OBJC)

add_library(pasteboard SHARED pasteboard.m)

# target_link_libraries(pasteboard "-framework AppKit")
find_library(APPKIT_LIB AppKit)
target_link_libraries(pasteboard ${APPKIT_LIB})

find_package(Python REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(pasteboard ${PYTHON_LIBRARIES})