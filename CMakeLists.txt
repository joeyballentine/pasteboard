cmake_minimum_required(VERSION 3.13 FATAL_ERROR)
set(CMAKE_FIND_LIBRARY_SUFFIXES ".m")

project(pasteboard LANGUAGES CXX OBJC)
set(CMAKE_C_FLAGS "-x objective-c")
enable_language(OBJC)

add_subdirectory("src/pasteboard")

include_directories("src/pasteboard")

# target_link_libraries(pasteboard "-framework AppKit")
find_library(APPKIT_LIB AppKit)
target_link_libraries(pasteboard PRIVATE ${APPKIT_LIB})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(pasteboard ${PYTHON_LIBRARIES})
