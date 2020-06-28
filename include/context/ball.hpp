#pragma once

#include "shared_memory/serializer.hpp"

#include <context/coordinates.hpp>
#include "context/state.hpp"
#include "context/velocity_compute.hpp"

namespace context
{
/*! Encapsulates the State of the ball (i.e. position and velocity).
 *  Compute the velocity of the ball using finite difference
 *  and low pass filtering.
 */
class Ball
{
public:
    /**
     *  @param size of the moving window for the low pass filtering
     *         of the velocity
     */
    Ball(int velocity_average_size);

    /**
     * Updates the state of the ball. The position value is replaced
     * by the parameter position value. The velocity is updated using
     * finite difference and low pass filtering.
     * @param the new position of the ball and related time stamp
     * @returns the updated state of the ball
     */
    const State& update(long time_stamp, const Coordinates& position);

    /**
     * @returns the state as computed the latest time update was called
     */
    const State& get();

    template <class Archive>
    void serialize(Archive& archive)
    {
        archive(state_, initialized_, previous_time_, velocity_computes_);
    }

private:
    friend shared_memory::private_serialization;

    // position and velocity of the ball
    State state_;

    // computes velocity based on position and time stamp
    // + low pass filter
    std::array<VelocityCompute, 3> velocity_computes_;

    // for velocity computation
    bool initialized_;
    long previous_time_;
};
}
