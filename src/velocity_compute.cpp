#include "context/velocity_compute.hpp"

namespace context
{
VelocityCompute::VelocityCompute() : previous_position_(0), initialized_(false)
{
}

VelocityCompute::VelocityCompute(int average_size)
    : filter_(average_size), previous_position_(0), initialized_(false)
{
}

void VelocityCompute::set_average_size(int average_size)
{
    filter_.set_average_size(average_size);
}

double VelocityCompute::get(long diff_time, double position)
{
    if (!initialized_)
    {
        previous_position_ = position;
        initialized_ = true;
    }
    double dx =
        (position - previous_position_) / static_cast<double>(diff_time);
    previous_position_ = position;
    return filter_.get(dx);
}
}
