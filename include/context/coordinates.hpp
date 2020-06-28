#pragma once

#include <array>

#include "shared_memory/serializer.hpp"

namespace context
{

    /* ! array of double of size 3, i.e. x, y and z */
    typedef std::array<double,3> Coordinates;

    /*! A time stamped coordinate*/
    class StampedCoordinates
    {
    public:
	
	/*3d coordinates, i.e. x, y and z*/
	Coordinates coordinates;

	/*time stamp*/
	long int stamp;

	template <class Archive>
	void serialize(Archive &archive)
	{
	    archive(coordinates,stamp);
	}

	
    };

}
