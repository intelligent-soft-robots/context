#include "gtest/gtest.h"

#include "context/low_pass_filter.hpp"
#include "context/velocity_compute.hpp"
#include "context/ball.hpp"

using namespace context;

class context_tests : public ::testing::Test
{};

TEST_F(context_tests, low_path_filter_default)
{
    LowPassFilter f;
    for(double i=0.0;i<1000.0;i+=1.0)
	{
	    double v = f.get(i);
	    ASSERT_EQ(i,v);
	}
}

TEST_F(context_tests, low_path_filter_single_value)
{
    LowPassFilter f(100);
    for(int i=0;i<1000;i++)
	{
	    double v = f.get(2.0);
	    ASSERT_EQ(v,2.0);
	}
}

TEST_F(context_tests, low_path_filter_manual_test_1)
{
    LowPassFilter f(100);
    for(double i=0.0;i<=4.0;i+=1.0)
	{
	    f.get(i);
	}
    double v = f.get(5.0);
    ASSERT_EQ(v,(0.0+1.0+2.0+3.0+4.0+5.0)/6.0);
}

TEST_F(context_tests, low_path_filter_manual_test_2)
{
    LowPassFilter f(4);
    for(double i=0.0;i<=4.0;i+=1.0)
	{
	    f.get(i);
	}
    double v = f.get(5.0);
    ASSERT_EQ(v,(2.0+3.0+4.0+5.0)/4.0);
}

TEST_F(context_tests, velocity_compute_no_motion)
{
    VelocityCompute vc;
    for(int i=0;i<1000;i++)
	{
	    double v = vc.get(10,1);
	    ASSERT_EQ(v,0);
	}
}

TEST_F(context_tests, velocity_compute_fixed_velocity)
{
    double position = 0;
    long int t_diff = 10;
    VelocityCompute vc;
    for(int i=0;i<1000;i++)
	{
	    double v = vc.get(t_diff,position);
	    position+=10.0;
	    if(i==0)
		{
		    ASSERT_EQ(v,0.0);
		}
	    else
		{
		    ASSERT_EQ(v,1.0);
		}
	}
}

TEST_F(context_tests, ball)
{
    long time_stamp = 0;
    long int t_diff = 10;
    Coordinates position = {0.0,0.0,0.0};
    Coordinates velocity = {0.1,0.2,0.3};
    Ball ball(1);

    for(int i=0;i<1000;i++)
	{
	    for(int i=0;i<3;i++)
		{
		    position[i]+=velocity[i]*static_cast<double>(t_diff);
		}
	    State s = ball.update(time_stamp,position);
	    time_stamp += t_diff;
	    if(i>=1)
		{
		    for(int i=0;i<3;i++)
			{
			    ASSERT_EQ(s.velocity[i],velocity[i]);
			    ASSERT_EQ(s.position[i],position[i]);
			}
		}
	}
}





