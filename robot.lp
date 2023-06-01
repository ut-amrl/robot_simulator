
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

% timeout (for now)

% #program init_states.

% is_in_room("robot", "start_loc", 0).
% % is_in_room("Arjun", "office", 0).
% id(0).
% id(1).
% #program rules.
% #const timeout = 4.
% #external id(0).
% #external id(1).

% is_in_room("robot", "start_loc", 0).

% id(X) :- ext(X).

% Transition rules

% goto changes loc of robot at next timestep
is_in_room("robot", B, T+1) :- go_to(B, T), 
                            is_in_room("robot", C, T), C!=B, 
                            % {T >= X : id(X)}, 
                            T < timeout.

% robot stays in same loc unless goto issued
is_in_room("robot", R, T+1) :- is_in_room("robot", R, T), 
                                not go_to(_, T), % goto R is no-op
                                % 1{T >= X : id},
                                % id, 
                                T < timeout. 

% other agents stay in same loc (no control over other agents for now)
is_in_room(A, R, T+1) :- is_in_room(A, R, T), 
                        % {T >= X : id(X)}, 
                        T < timeout, 
                        A!="robot".

% if agents are in the same room, ask question
asked(Agent, Question, Time) :- is_in_room(Agent, Room, Time), 
                            is_in_room("robot", Room, Time),
                            ask(Agent, Question, Time), 
                            Agent != "robot".


% response(Answer) :- r(Answer).

% if agent asked question, get response
replied(Agent, Answer, Time) :- asked(Agent, Question, Time),
                                r(Answer).


% #program nl_commands.
% id(0).
% id(1).
% is_in_room("robot", "start_loc", 0).