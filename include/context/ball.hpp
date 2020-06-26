#pragma once

#include <context/coordinates.hpp>
#include "context/velocity_compute.hpp"
#include "context/state.hpp"

namespace context
{

    class Ball
    {
    public:
	Ball(int velocity_average_size);
	const State& update(long time_stamp, const Coordinates& position);
    private:
	State state_;
	std::array<VelocityCompute,3> velocity_computes_;
	bool initialized_;
	long previous_time_;
    };
    

}
