% ASP lightweight simulator for evaluating robot command traces
% INPUT: NL command and generated code
% eg.
%   "Go to Arjun's office, ask him if he is ready to head out, and come back and tell me what he said"
%    ```
%     start_loc = get_current_loc()
%     go_to("Arjun's office")
%     response = ask("Arjun", "ready to head out?", ["yes", "no", "maybe"])
%     go_to(start_loc)
%     say("Arjun said: " + response)
%   ```
% OUTPUT: whether generated code matches NL command
% METHOD: run a simulation of the code, check if it meets the NL command specifications

#program init_states.

% stuff added here from NL command

#program rules.

1{ response(Answer) : r(Answer)}1.


% Transition rules

% goto changes loc of robot at next timestep
is_in_room("robot", B, I+1) :- go_to(B, I), is_in_room("robot", C, I), C!=B, I+1 < tmax.

% robot stays in same loc unless goto issued
is_in_room("robot", R, T+1) :- is_in_room("robot", R, T), T+1<tmax, 
                    not go_to(_, T). 

% other agents stay in same loc (no control over other agents for now)
is_in_room(A, R, T+1) :- is_in_room(A, R, T), T+1<tmax, A!="robot".

% if agents are in the same room, ask question
asked(Agent, Question, Time) :- is_in_room(Agent, Room, Time), 
                            is_in_room("robot", Room, Time),
                            ask(Agent, Question, Time), Agent != "robot".

% if agent asked question, get response
replied(Agent, Answer, Time+1) :- asked(Agent, Question, Time),
                                response(Answer).


#program nl_commands.
