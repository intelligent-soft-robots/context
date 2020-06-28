#pragma once

#include <deque>

#include "shared_memory/serializer.hpp"

namespace context
{
/*! Implements a low pass filter via a moving window average.
 *  By default the moving window size is of 1, i.e. no filtering.
 */
class LowPassFilter
{
public:
    LowPassFilter();

    /**
     * Set a filter with the specified moving window size
     */
    LowPassFilter(int average_size);

    /**
     * Reset the moving averaging window size to a new value.
     * Call to this function may impact real time.
     */
    void set_average_size(int average_size);

    /**
     * Apply the filter
     */
    double get(double value);

    template <class Archive>
    void serialize(Archive &archive)
    {
        archive(average_size_, values_, sum_);
    }

private:
    int average_size_;
    std::deque<double> values_;
    double sum_;
};
}
