

class HitPoint:

    def __init__(self,table_height,default_position=[-10,-10,-10]):
        self._table_height = table_height
        self._default_position = default_position
        self._hit_position = None

    def reset(self):
        self._hit_position = None
        
    def update(self,ball_position,
               racket_contact_information):
        if self._hit_position is not None:
            return self._hit_position
        hit_racket = False
        if racket_contact_information.contact_occured:
            hit_racket = True
        if not hit_racket:
            return self._default_position
        if hit_racket:
            if ball_position[2] < (self._table_height+0.02):
                self._hit_position = ball_position
                return self._hit_position
        return self._default_position
                
