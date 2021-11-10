#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "context/ball.hpp"
#include "context/contact_information.hpp"
#include "context/coordinates.hpp"
#include "context/low_pass_filter.hpp"
#include "context/rotation.hpp"
#include "context/state.hpp"
#include "context/transform.hpp"
#include "context/velocity_compute.hpp"
#include "shared_memory/shared_memory.hpp"

using namespace context;

PYBIND11_MODULE(context_wrp, m)
{
    pybind11::class_<Coordinates>(m, "Coordinates").def(pybind11::init<>());

    pybind11::class_<StampedCoordinates>(m, "StampedCoordinates")
        .def(pybind11::init<>())
        .def_readwrite("coordinates", &StampedCoordinates::coordinates)
        .def_readwrite("stamp", &StampedCoordinates::stamp);

    pybind11::class_<VelocityCompute>(m, "VelocityCompute")
        .def(pybind11::init<>())
        .def(pybind11::init<int>())
        .def("set_average_size", &VelocityCompute::set_average_size)
        .def("get", &VelocityCompute::get);

    pybind11::class_<LowPassFilter>(m, "LowPassFilter")
        .def(pybind11::init<>())
        .def(pybind11::init<int>())
        .def("set_average_size", &LowPassFilter::set_average_size)
        .def("get", &LowPassFilter::get);

    pybind11::class_<State>(m, "State")
        .def(pybind11::init<>())
        .def(pybind11::init<const Coordinates&, const Coordinates&>())
        .def_readwrite("position", &State::position)
        .def_readwrite("velocity", &State::velocity)
        .def("set_position", &State::set_position)
        .def("set_velocity", &State::set_velocity);

    pybind11::class_<Ball>(m, "Ball")
        .def(pybind11::init<int>())
        .def("update", &Ball::update)
        .def("get", &Ball::get);

    pybind11::class_<Rotation>(m, "Rotation")
        .def(pybind11::init<double, double, double>())
        .def("rotate", &Rotation::rotate);

    pybind11::class_<Transform>(m, "Transform")
        .def(pybind11::init<double, double, double, Coordinates>())
        .def("apply", &Transform::apply);

    pybind11::class_<ContactInformation>(m, "ContactInformation")
        .def(pybind11::init<>())
        .def_readonly("position", &ContactInformation::position)
        .def_readonly("contact_occured", &ContactInformation::contact_occured)
        .def_readonly("time_stamp", &ContactInformation::time_stamp)
        .def_readonly("minimal_distance",
                      &ContactInformation::minimal_distance);
}
