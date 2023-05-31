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

room("Arjuns_office").
room("start_loc").
agent("robot").
agent("Arjun").
is_in("Arjun", "Arjuns_office", 0).
is_in("robot", "start_loc", 0).

r("no"). r("yes"). r("maybe").
1{ response(Answer) : r(Answer)}1.
#const tmax = 5.

% Transition rules

% goto changes loc at next timestep
is_in("robot", B, I+1) :- go_to(B, I), is_in("robot", C, I), C!=B, I+1 < tmax.

% stays in same loc unless goto issued
is_in(A, R, T+1) :- is_in(A, R, T), T+1<tmax, 
                    not go_to(X, T), room(X). % no two places

% if agents in same room, ask question
asked(Agent, Question, Time) :- is_in(Agent, Room, Time), 
                            is_in("robot", Room, Time),
                            ask(Agent, Question, Time), Agent != "robot".

% if agent asked question, get response
replied(Agent, Answer, Time+1) :- asked(Agent, Question, Time),
                                response(Answer).

% LLM Generated code (translated):
go_to("Arjuns_office", 0).
ask("Arjun", "ready to head out?", 1).
% go_to("start_loc", 3).

% Test cases require NL goals : get Arjun's reply, come back to start loc
:- not replied("Arjun", _, _).
:- not is_in("robot", "start_loc", tmax-1).
