import math

def _distance(p1,p2):
    return math.sqrt(sum([(p2_-p1_)**2
                          for p1_,p2_ in zip(p1,p2)]))


def _norm(p):
    return math.sqrt(sum([p_**2 for p_ in p]))


class BallStatus:

    def __init__(self,
                 target_position):
        
        self.target_position = target_position
        self.reset()
        
    def reset(self):

        self.min_distance_ball_racket = float("+inf") # will be None if ball hit the racket
        self.min_distance_ball_target = float("+inf")
        self.max_ball_velocity = 0
        self.table_contact_position = None
        self.min_z = float("+inf")
        self.max_y = float("-inf")
        self.ball_position = [None]*3
        self.ball_velocity = [None]*3
        
    def update(self,
               ball_position,
               ball_velocity,
               racket_contact_information): # instance of context.ContactInformation

        self.ball_position = ball_position
        self.ball_velocity = ball_velocity
        
        # updating lowest and furthest ever observed position
        # of the ball
        self.min_z = min(ball_position[2],self.min_z)
        self.max_y = max(ball_position[1],self.max_y)

        # updating min distance ball/racket
        hit_racket = False
        if racket_contact_information.contact_occured:
            self.min_distance_ball_racket = None
            hit_racket = True
        else :
            self.min_distance_ball_racket = racket_contact_information.minimal_distance

        # if post contact with racket, updating min distance ball/target
        if hit_racket:
            d = _distance(self.ball_position,self.target_position)
            self.min_distance_ball_target = min(d,self.min_distance_ball_target)

        # if post contact with racket, updating max ball velocity
        if hit_racket:
            v = _norm(self.ball_velocity)
            self.max_ball_velocity = max(self.max_ball_velocity,v)
        
