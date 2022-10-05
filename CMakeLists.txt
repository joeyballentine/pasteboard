cmake_minimum_required(VERSION 3.13 FATAL_ERROR)
set(CMAKE_FIND_LIBRARY_SUFFIXES ".m")

project(pasteboard)

add_subdirectory("src/pasteboard")

include_directories("src/pasteboard")