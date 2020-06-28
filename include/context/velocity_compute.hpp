#pragma once

#include "shared_memory/serializer.hpp"

#include "context/low_pass_filter.hpp"

namespace context
{

    /*! Computes the velocity using finite difference
     *  over the position and low pass filtering.
     *  The default moving window size for low pass filtering
     *  is 1, i.e. no filtering.
     */
    class VelocityCompute
    {
    public:
	
	VelocityCompute();
	/**
	 * Set the size of the moving window 
	 * for low pass filtering
	 */
	VelocityCompute(int average_size);

	/** Reset the size of the moving window
	 * for low pass filtering */
	void set_average_size(int average_size);

	/** Apply finit difference and low pass filtering, 
	 *  and return the computed velocity */ 
	double get(long diff_time, double position);

	template <class Archive>
	void serialize(Archive &archive)
	{
	    archive(filter_,previous_position_,
		    initialized_);
	}
	
    private:
	// low pass filter
	LowPassFilter filter_;

	// for finite difference
	double previous_position_;
	bool initialized_;
    };

}
