#pragma once

#include "context/rotation.hpp"

namespace context
{
/*! 3d homogeneous transformation */
class Transform
{
public:
    /**
     * Construct the transformation matrix
     * @param alpha: rotation around x
     * @param beta: rotation around y
     * @param gamma: rotation around z
     * @param translation: translation
     */
    Transform(double alpha, double beta, double gamma, Coordinates translation);
    /**
     * Apply the transformation to coordinates
     */
    void apply(Coordinates& coordinates);

private:
    Rotation rotation_;
    Coordinates translation_;
};

}  // namespace context
