#pragma once

#include "shared_memory/serializer.hpp"

#include "context/coordinates.hpp"

namespace context
{

    /*! Encapsulate the 3d position and the 3d 
     *  velocity of an object.
     */
    class State
    {
    public:

	State();
	Coordinates position;
	Coordinates velocity;

	template <class Archive>
	void serialize(Archive &archive)
	{
	    archive(position,velocity);
	}
	
    };
    
}
