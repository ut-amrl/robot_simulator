from clingo import Control, ast
from clingo.solving import Model
from clingo.symbol import Function, String, Number
from typing import List 

class Context:

    def __init__(self, robot_cmds_file = "robot.lp"):
        self.ctl = Control()
        self.ctl.load(robot_cmds_file)
        self.parts = [("init_states", []),("rules", []), ("nl_commands", [])]
        self.curr_tp = 0

    def solve(self):
        return self.ctl.solve()

    def ground_to_latest_tp(self) -> None:
        # ground to latest time point
        self.ctl.ground([self.parts[0], self.parts[2]])
        self.ctl.solve()
        self.ctl.ground([self.parts[1]])
        self.ctl.solve()
        
    def get_curr_timestep(self) -> int:
        # gets max time (from latest NL cmd)
        self.ctl.ground([self.parts[0], self.parts[2]])
        all_cmds_tps = []
        for (sig, arity, _) in self.ctl.symbolic_atoms.signatures:
            all_cmds_tps += [int(str(func.symbol.arguments[2])) for func
                             in self.ctl.symbolic_atoms.by_signature(sig, arity)]
        
        print(all_cmds_tps, self.ctl.symbolic_atoms.signatures)
        
        return max(all_cmds_tps)
    
    def get_current_location(self) -> str:
        # get robot location at max time (from is_in_room)
        time_step = self.get_curr_timestep()
        return self.get_room_at(time_step)

    def get_room_at(self, time : int, agent : str = "robot") -> str:
        room = [sig.symbol for sig 
                            in self.ctl.symbolic_atoms.by_signature("is_in_room", 3)
                            if sig.symbol.arguments[2] == Number(time) and
                            sig.symbol.arguments[0] == String(agent)]
        assert(len(room) == 1), room
        return str(room[0]).strip("\"")
    
    def get_all_rooms(self) -> List[str]:
        # get all "is in room" and "goto" values 
        self.ctl.ground([self.parts[0], self.parts[2]])
        is_in_room_stmts = [str(sig.symbol.arguments[1]) for sig 
                            in self.ctl.symbolic_atoms.by_signature("is_in_room", 3)]
        goto_stmts = [str(sig.symbol.arguments[1]) for sig 
                            in self.ctl.symbolic_atoms.by_signature("go_to", 2)]
        
        return is_in_room_stmts + goto_stmts
    
    
    
    def is_in_room(self, obj : str) -> bool:
        # check if is in the room at curr time step
        time = self.get_curr_timestep()
        room = self.get_room_at(time)
        self.ctl.ground([self.parts[0]])
        
        return any((str(i.symbol.arguments[0]) == f'"{obj}"' and   
                        str(i.symbol.arguments[1]) == f'"{room}"' and
                        int(str(i.symbol.arguments[2])) == time) for i in 
                self.ctl.symbolic_atoms.by_signature("is_in_room", 3))

    def go_to(self, location : str) -> None:
        # issue goto
        self.ctl.add("nl_commands", [], f'go_to("robot", "{location}", {self.get_curr_timestep() + 1}).')

    def ask(self, person : str, question : str, options: List[str]) -> str:
        pass
        # issue ask and r() options, get reply at T+1
        
    def say(self, message : str) -> None:
        pass
        # issue say

def main():
    c = Context()
    # NL command:
    c.ctl.add("init_states", [], 'is_in_room("robot", "start_loc", 0).')
    c.ctl.add("init_states", [], 'is_in_room("Arjun", "office", 0).')
    c.ctl.add("")
    # generated LLM code:
    start_loc = c.get_current_location()
    print(start_loc)
    # print(c.is_in_room("robot"))
    # c.go_to("Arjun's office")
    # print(c.get_current_location())
    print(c.get_room_at(0))
    # print(c.is_in_room("robot"))
    # response = ask("Arjun", "Are you ready to go?", ["Yes", "No"])
    # c.go_to("start_loc")
    # print(c.get_current_location())
    # say("Arjun said: " + response)

if __name__=="__main__":
    main()
    
# % Test cases require NL goals : get Arjun's reply, come back to start loc
# :- not replied("Arjun", _, _).
# :- not is_in_room("robot", "start_loc", tmax-1).

# % LLM Generated code (translated):
# go_to("Arjuns_office", 0).
# ask("Arjun", "ready to head out?", 1).
# go_to("start_loc", 3).
