#include "context/rotation.hpp"

namespace context
{

  Rotation::Rotation(double alpha,
	     double beta,
	     double gamma)
    {
      Eigen::Matrix3d rx,ry,rz;
      rx(0,0)=1;
      rx(0,1)=0;
      rx(0,2)=0;
      rx(1,0)=0;
      rx(1,1)=cos(alpha);
      rx(1,2)=sin(alpha);
      rx(2,0)=0;
      rx(2,1)=-sin(alpha);
      rx(2,2)=cos(alpha);
      ry(0,0)=cos(beta);
      ry(0,1)=0;
      ry(0,2)=-sin(beta);
      ry(1,0)=0;
      ry(1,1)=1;
      ry(1,2)=0;
      ry(2,0)=sin(beta);
      ry(2,1)=0;
      ry(2,2)=cos(beta);
      rz(0,0)=cos(gamma);
      rz(0,1)=sin(gamma);
      rz(0,2)=0;
      rz(1,0)=-sin(gamma);
      rz(1,1)=cos(gamma);
      rz(1,2)=0;
      rz(2,0)=0;
      rz(2,1)=0;
      rz(2,2)=1;
      rotation_ = rx * ry * rz; 
    }
  
  void Rotation::rotate(Coordinates& coordinates)
  {
    Eigen::Vector3d v(coordinates.data());
    v = rotation_*v;
    coordinates[0]=v[0];
    coordinates[1]=v[1];
    coordinates[2]=v[2];
  }

};
