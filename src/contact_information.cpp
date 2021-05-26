#include "context/contact_information.hpp"

namespace context
{
  ContactInformation::ContactInformation()
    : position{0,0,0},
      contact_occured{false},
      time_stamp{-1},
      minimal_distance{-1},
      disabled{false}
  {}

  void ContactInformation::register_distance(double d)
  {
    if(minimal_distance<0)
      {
	minimal_distance=d;
	return;
      }
    minimal_distance = std::min(minimal_distance,
				d);
  }

  void ContactInformation::register_contact(std::array<double,3> _position,
					    double _time_stamp)
  {
    contact_occured=true;
    minimal_distance = 0;
    position = _position;
    time_stamp = _time_stamp;
  }

}
