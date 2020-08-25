#pragma once

#include <sstream>
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
  State(const Coordinates& position,
	const Coordinates& velocity);
  void set(const Coordinates& position,
	   const Coordinates& velocity);
  std::array<Coordinates,2> get() const;
  std::string to_string() const;
  void set_position(double x, double y, double z);
  void set_velocity(double x, double y, double z);
  Coordinates position;
  Coordinates velocity;

  template <class Archive>
  void serialize(Archive &archive)
  {
    archive(position, velocity);
  }
};
}  // namespace context
