cmake_minimum_required(VERSION 2.8.7)

project(context)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

find_package(catkin REQUIRED COMPONENTS
  pybind11_catkin
  shared_memory
)

DEFINE_OS()

catkin_package(
 LIBRARIES context
 INCLUDE_DIRS include
 CATKIN_DEPENDS pybind11_catkin shared_memory
)

include_directories(include ${catkin_INCLUDE_DIRS})

add_library(context
  src/velocity_compute.cpp
  src/ball.cpp)
target_link_libraries(context ${catkin_LIBRARIES})

