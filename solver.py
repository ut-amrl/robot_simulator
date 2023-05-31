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

 
    def solve_to_tp(self, tp: int) -> None:
        # ground to tp
        self.ctl.ground(self.parts + [("base",f"#const tmax = {tp}.")])
        self.ctl.solve()
        
        
    def get_current_location(self) -> str:
        # get robot location at max time (from is_in_room)
        time_step = self.curr_tp
        return self.get_room_at(time_step)

    def get_room_at(self, time : int, agent : str = "robot") -> str:
        self.solve_to_tp(time)
        room = [sig.symbol for sig 
                            in self.ctl.symbolic_atoms.by_signature("is_in_room", 3)
                            if sig.symbol.arguments[2] == Number(time) and
                            sig.symbol.arguments[0] == String(agent)]
        assert(len(room) == 1), room
        return str(room[0]).strip("\"")
    
    def get_all_rooms(self) -> List[str]:
        # get all "is in room" and "goto" values 
        self.solve_to_tp(self.curr_tp)
        is_in_room_stmts = [str(sig.symbol.arguments[1]) for sig 
                            in self.ctl.symbolic_atoms.by_signature("is_in_room", 3)]
        goto_stmts = [str(sig.symbol.arguments[1]) for sig 
                            in self.ctl.symbolic_atoms.by_signature("go_to", 2)]
        
        return is_in_room_stmts + goto_stmts
    
    
    def is_in_room(self, obj : str) -> bool:
        # check if is in the room at curr time step
        room = self.get_room_at(self.curr_tp)

        return any((str(i.symbol.arguments[0]) == f'"{obj}"' and   
                        str(i.symbol.arguments[1]) == f'"{room}"' and
                        int(str(i.symbol.arguments[2])) == self.curr_tp) for i in 
                self.ctl.symbolic_atoms.by_signature("is_in_room", 3))

        
    ## actions: ground after each action
    
    ## get most curr response
    def say(self, message : str) -> None:
        # get most current reply
        reply = [reply[1] for reply in self.ctl.symbolic_atoms.by_signature("replied", 3)
                 if reply.symbol.arguments[2] == self.curr_tp]
        assert(len(reply) == 1), reply
        print(message + reply)
        
    def go_to(self, location : str) -> None:
        # issue goto
        self.ctl.add("nl_commands", [], f'go_to("robot", "{location}", {self.curr_tp + 1}).')
        self.curr_tp += 1
        self.solve_to_tp(self.curr_tp)

    def ask(self, person : str, question : str, options: List[str]) -> str:
        # issue ask and r() options, get reply at T+1
        for opt in options:
            self.ctl.add("init_states", [], f"r({opt}).")
        self.ctl.add("nl_commands", [], f'ask("{person}", "{question}", {self.curr_tp + 1}).')
        self.curr_tp += 1
        self.solve_to_tp(self.curr_tp)
        
    

def main():
    c = Context()
    # NL command:
    c.ctl.add("init_states", [], 'is_in_room("robot", "start_loc", 0).')
    c.ctl.add("init_states", [], 'is_in_room("Arjun", "office", 0).')
    c.ctl.add("")
    # generated LLM code:
    loc1 = c.get_current_location()
    print(loc1)
    # tp1 = c.curr_tp
    # c.go_to("Arjun's office")
    # loc2 = c.get_current_location()
    # tp2 = c.curr_tp
    # assert(loc1 == "start_loc"), loc1
    # assert(loc2 == "Arjun's office"), loc2
    # assert(tp1 == 0), tp1
    # assert(tp2 == 1), tp2


if __name__=="__main__":
    main()
    
# % Test cases require NL goals : get Arjun's reply, come back to start loc
# :- not replied("Arjun", _, _).
# :- not is_in_room("robot", "start_loc", tmax-1).

# % LLM Generated code (translated):
# go_to("Arjuns_office", 0).
# ask("Arjun", "ready to head out?", 1).
# go_to("start_loc", 3).
