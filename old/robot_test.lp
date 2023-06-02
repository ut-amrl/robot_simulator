#const timeout = 4.
#include <incmode>.

#external id(0).
#external id(1).
#external id(2).
#external id(3).    


% Transition rules


% goto changes loc of robot at next timestep
is_in_room("robot", B, T+1) :- go_to(B, T), 
                            is_in_room("robot", C, T), C!=B,
                            X =  #max {XX,1:id(XX)}, 
                            T < X, 
                            T < timeout.

% robot stays in same loc unless goto issued
is_in_room("robot", R, T+1) :- is_in_room("robot", R, T), 
                                not go_to(_, T), % goto R is no-op
                                X =  #max {XX,1:id(XX)}, 
                                T < X, 
                                T < timeout.

#program time(t).

#external id(t+1).
#external id(t+2).
#external id(t+3). 

is_in_room("robot", B, T+1) :- go_to(B, T), 
                            is_in_room("robot", C, T), C!=B,
                            X =  #max {XX,1:id(_, XX)}, 
                            T >= t,
                            T < X, 
                            T < timeout.

% robot stays in same loc unless goto issued
is_in_room("robot", R, T+1) :- is_in_room("robot", R, T), 
                                not go_to(_, T), % goto R is no-op
                                X =  #max {XX,1:id(XX)}, 
                                T >= t,
                                T < X, 
                                T < timeout.