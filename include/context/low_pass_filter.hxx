
template<typename T>
LowPassFilter<T>::LowPassFilter()
    : average_size_(1),
      sum_(0)
{}

template<typename T>
LowPassFilter<T>::LowPassFilter(int average_size)
    : average_size_(average_size),
      sum_(0)
{}

template<typename T>
void LowPassFilter<T>::set_average_size(int average_size)
{
    average_size_ = average_size;
}

template<typename T>
T LowPassFilter<T>::get(T value)
{
    if (values_.size()==average_size_)
	{
	    sum_ -= values_.front();
	    values_.pop_front();
	}
    sum_+=value;
    return sum_/static_cast<T>(values_.size());
}


