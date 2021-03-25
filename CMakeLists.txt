cmake_minimum_required(VERSION 3.10.2)

project(context)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED on)


################
# Dependencies #
################

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(mpi_cmake_modules REQUIRED)
find_package(pybind11 REQUIRED)
find_package(shared_memory REQUIRED)
ament_export_dependencies(
  pybind11
  shared_memory)

# prepare to export all needed targets
set(all_targets)
set(all_target_exports)


#######################
# Configuration files #
#######################

get_filename_component(TRAJECTORIES_DIR trajectories ABSOLUTE)
install(DIRECTORY "${TRAJECTORIES_DIR}"
  DESTINATION /opt/mpi-is/context)
install(DIRECTORY "${TRAJECTORIES_DIR}"
  DESTINATION opt/mpi-is/context)


###########
# Library #
###########

add_library(${PROJECT_NAME} SHARED
  src/contact_information.cpp
  src/velocity_compute.cpp
  src/state.cpp
  src/ball.cpp
  src/low_pass_filter.cpp
  src/rotation.cpp
  src/transform.cpp)
target_include_directories(
  ${PROJECT_NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
ament_target_dependencies(${PROJECT_NAME} shared_memory)
target_link_libraries(${PROJECT_NAME} shared_memory::shared_memory)
ament_export_interfaces(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
list(APPEND all_targets ${PROJECT_NAME})
list(APPEND all_target_exports export_${PROJECT_NAME})


###################
# Python wrappers #
###################

add_library(${PROJECT_NAME}_wrp MODULE srcpy/wrappers.cpp)
target_link_libraries(${PROJECT_NAME}_wrp PRIVATE pybind11::module)
target_link_libraries(${PROJECT_NAME}_wrp PRIVATE ${PYTHON_LIBRARIES})
target_link_libraries(${PROJECT_NAME}_wrp PRIVATE ${PROJECT_NAME})
set_target_properties(${PROJECT_NAME}_wrp
                      PROPERTIES PREFIX "" SUFFIX "${PYTHON_MODULE_EXTENSION}")
target_include_directories(
  ${PROJECT_NAME}_wrp
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
         $<INSTALL_INTERFACE:include> SYSTEM
  PUBLIC ${PYTHON_INCLUDE_DIRS})
_ament_cmake_python_get_python_install_dir()
install(TARGETS ${PROJECT_NAME}_wrp DESTINATION ${PYTHON_INSTALL_DIR})


######################
# Python Native code #
######################

ament_python_install_package(${PROJECT_NAME} PACKAGE_DIR python/${PROJECT_NAME})


##############
# Unit tests #
##############

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_${PROJECT_NAME}_cpp tests/main.cpp tests/unit_tests.cpp)
  target_link_libraries(test_${PROJECT_NAME}_cpp ${PROJECT_NAME})
endif()


######################
# Install and export #
######################

install(DIRECTORY include/ DESTINATION include)
install(
  TARGETS ${all_targets}
  EXPORT ${all_target_exports}
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES
  DESTINATION include)
ament_package()




