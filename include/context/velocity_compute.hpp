#pragma once

#include "context/low_pass_filter.hpp"

namespace context
{

    class VelocityCompute
    {
    public:	
	VelocityCompute();
	VelocityCompute(int average_size);
	void set_average_size(int average_size);
	double get(long diff_time, double position);
    private:
	LowPassFilter<double> filter_;
	double previous_position_;
	bool initialized_;
    };

}
