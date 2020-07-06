#include "context/transform.hpp"

namespace context
{

  Transform::Transform(double alpha, double beta, double gamma,
	      Coordinates translation)
      : rotation_(alpha,beta,gamma),
	translation_(translation)
    {}
  
  void Transform::apply(Coordinates& coordinates)
    {
      rotation_.rotate(coordinates);
      for(int i=0;i<3;i++)
	{
	  coordinates[i]+=translation_[i];
	}
    }
  
}
