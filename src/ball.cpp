#include "context/ball.hpp"

namespace context
{
Ball::Ball(int velocity_average_size) : initialized_(false), previous_time_(-1)
{
    for (VelocityCompute& velocity_compute : velocity_computes_)
    {
        velocity_compute.set_average_size(velocity_average_size);
    }
}

const State& Ball::update(long time_stamp, const Coordinates& position)
{
    state_.position = position;
    if (!initialized_)
    {
        previous_time_ = time_stamp;
        initialized_ = true;
    }
    long time_diff = time_stamp - previous_time_;
    previous_time_ = time_stamp;
    for (int i = 0; i < 3; i++)
    {
        state_.velocity[i] = velocity_computes_[i].get(time_diff, position[i]);
    }
    return state_;
}

const State& Ball::get()
{
    return state_;
}
}  // namespace context
