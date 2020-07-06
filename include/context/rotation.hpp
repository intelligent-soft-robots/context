#pragma once

#include <eigen3/Eigen/Core>
#include <cmath>

#include "context/coordinates.hpp"

namespace context
{

  /* ! A 3d rotation */
  class Rotation
  {
  public:
    /**
     * Construct the rotation matrix.
     * @param alpha: rotation around x 
     * @param beta: rotation around y
     * @param gamma: rotation around z 
     */
    Rotation(double alpha,
	     double beta,
	     double gamma);
    /**
     * Apply the rotation to coordinates
     */
    void rotate(Coordinates& coordinates);
  private:
    Eigen::Matrix3d rotation_;
  };
  
}

