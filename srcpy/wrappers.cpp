#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "context/ball.hpp"
#include "context/low_pass_filter.hpp"
#include "context/state.hpp"
#include "context/coordinates.hpp"
#include "context/velocity_compute.hpp"

using namespace context;

PYBIND11_MODULE(context,m)
{

    pybind11::class_<Coordinates>(m,"Coordinates")
	.def(pybind11::init<>());

    pybind11::class_<StampedCoordinates>(m,"StampedCoordinates")
	.def(pybind11::init<>())
	.def_readwrite("coordinates",&StampedCoordinates::coordinates)
	.def_readwrite("stamp",&StampedCoordinates::stamp);

    pybind11::class_<VelocityCompute>(m,"VelocityCompute")
	.def(pybind11::init<>())
	.def(pybind11::init<int>())
	.def("set_average_size",&VelocityCompute::set_average_size)
	.def("get",&VelocityCompute::get);
	
    pybind11::class_<LowPassFilter>(m,"LowPassFilter")
	.def(pybind11::init<>())
	.def(pybind11::init<int>())
	.def("set_average_size",&LowPassFilter::set_average_size)
	.def("get",&LowPassFilter::get);

    pybind11::class_<State>(m,"State")
	.def(pybind11::init<>())
	.def_readwrite("position",&State::position)
	.def_readwrite("velocity",&State::velocity);

    pybind11::class_<Ball>(m,"Ball")
	.def(pybind11::init<int>())
	.def("update",&Ball::update)
	.def("get",&Ball::get);
    
}
