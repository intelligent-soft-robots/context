#include "context/low_pass_filter.hpp"

namespace context
{
LowPassFilter::LowPassFilter() : average_size_(1), sum_(0)
{
    values_.resize(1);
}

LowPassFilter::LowPassFilter(int average_size)
    : average_size_(average_size), sum_(0)
{
}

void LowPassFilter::set_average_size(int average_size)
{
    average_size_ = average_size;
    values_.resize(average_size);
}

double LowPassFilter::get(double value)
{
    if (average_size_ == 1)
    {
        return value;
    }
    if (values_.size() == average_size_)
    {
        sum_ -= values_.front();
        values_.pop_front();
    }
    sum_ += value;
    values_.push_back(value);
    return sum_ / static_cast<double>(values_.size());
}
}  // namespace context
