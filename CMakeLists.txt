cmake_minimum_required(VERSION 2.8.7)

project(context)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

find_package(catkin REQUIRED COMPONENTS
  pybind11_catkin
  shared_memory
  mpi_cmake_modules
)
search_for_eigen()

# detecting if "normal" or realtime OS
DEFINE_OS()

catkin_package(
 LIBRARIES context
 INCLUDE_DIRS include
 CATKIN_DEPENDS pybind11_catkin shared_memory mpi_cmake_modules
)

include_directories( include
                     ${catkin_INCLUDE_DIRS}
                     ${Eigen_INCLUDE_DIRS} )

# creating library
add_library(context
  src/velocity_compute.cpp
  src/ball.cpp
  src/low_pass_filter.cpp
  src/rotation.cpp
  src/transform.cpp)
target_link_libraries(context ${catkin_LIBRARIES})

# python wrappers
# note: the generated package is context_wrp.
# the context package (generated based on the content of python/context)
# will be extended using the content of context_wrp.
# In practice, python users code should just import "context"
pybind11_add_module(context_py srcpy/wrappers.cpp)
target_link_libraries(context_py PRIVATE context ${catkin_LIBRARIES})
set_target_properties(context_py PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CATKIN_DEVEL_PREFIX}/${CATKIN_GLOBAL_PYTHON_DESTINATION}
  OUTPUT_NAME context_wrp)
install(TARGETS context_py DESTINATION ${CATKIN_GLOBAL_PYTHON_DESTINATION})

# python package (will be extended with context_wrp)
catkin_python_setup()

# unit tests
catkin_add_gtest(context_unit_tests
  tests/main.cpp
  tests/unit_tests.cpp)
target_link_libraries(context_unit_tests context ${catkin_libraries})

# documentation 
build_sphinx_documentation()
