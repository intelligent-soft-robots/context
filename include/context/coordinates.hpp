#pragma once

#include <array>

namespace context
{

    typedef std::array<double,3> Coordinates;

    class StampedCoordinates
    {
    public:
	Coordinates coordinates;
	long int stamp;
    };

}
