#include "context/state.hpp"

namespace context
{

  State::State()
  {
  }
  
  State::State(const Coordinates& position_,
	const Coordinates& velocity_)
    : position(position_),
      velocity(velocity_){}

  void State::set(const Coordinates& position_,
		  const Coordinates& velocity_)
  {
    position = position_;
    velocity = velocity_;
  }

  std::array<Coordinates,2> State::get() const
  {
    std::array<Coordinates,2> r = {position,velocity};
    return r;
  }

  std::string State::to_string() const
  {
    std::stringstream ss;
    for (int i=0;i<3;i++)
      {
	ss << position[i] << " (" << velocity[i] << ") ";
      }
    return ss.str();
  }
  
  void State::set_position(double x, double y, double z)
  {
    position[0]=x;
    position[1]=y;
    position[2]=z;
  }

  void State::set_velocity(double x, double y, double z)
  {
    velocity[0]=x;
    velocity[1]=y;
    velocity[2]=z;
  }
  
}
