#pragma once

#include "context/coordinates.hpp"

namespace context
{

    class State
    {
    public:
	State();
	Coordinates position;
	Coordinates velocity;
    };
    
}
