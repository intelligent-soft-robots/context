#pragma once

#include <deque>

namespace context
{

    template<typename T>
    class LowPassFilter
    {
    public:
	LowPassFilter();
	LowPassFilter(int average_size);
	void set_average_size(int average_size);
	T get(T value);
    private:
	int average_size_;
	std::deque<T> values_;
	T sum_;
    };

    #include "low_pass_filter.hxx"
}
