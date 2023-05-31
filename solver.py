from clingo import Control, ast
from clingo.solving import Model
from clingo.symbol import Function, String, Number
from typing import List 
import clingo

class Context:

    def __init__(self, robot_cmds_file = "robot.lp", timeout=10):
        self.ctl = Control()
        self.ctl.load(robot_cmds_file)
        # self.parts = [("init_states", []),("rules", []), ("nl_commands", [])]
        self.ctl.add(f"#const timeout = {timeout}.")
        for i in range(timeout):
            self.ctl.add(f"#external ext{i}.")
        
        self.ctl.add("id(0) :- ext0.")
        self.curr_tp = 0

    # def release(self, a:int, b:int):
    #     for i in range(a, b):
    #         self.ctl.release_external(f"ext{i}")
    #     self.ctl.cleanup()
        
    def inc_curr_tp(self):
        self.curr_tp += 1
        self.ctl.add(f"id({self.curr_tp}) :- ext{self.curr_tp}.")

    def ground_and_solve(self):
        self.ctl.ground()
        return self.ctl.solve()

 
    # def solve_to_tp(self, tp: int) -> None:
    #     # ground to tp
    #     self.ctl.add(f"id({tp}) :- ext{tp}.")
    #     self.ctl.ground(self.parts)
    #     func = clingo.Function("id", [Number(tp)])
    #     assert(self.ctl.symbolic_atoms[func] is not None), tp
 
    #     # func = clingo.Function("id", [Number(0)])
    #     # print(func)
    #     assert(self.ctl.symbolic_atoms[func] is not None)
    #     self.ctl.solve()
        
    def debug_model(self):
        model = []
        with self.ctl.solve(yield_=True) as hnd:
            for i,m in enumerate(hnd):
                model.append(str(m))

        return model
            
    def get_current_location(self) -> str:
        # get robot location at max time (from is_in_room)
        time_step = self.curr_tp
        return self.get_room_at(time_step)

    def get_room_at(self, time : int, agent : str = "robot") -> str:
        self.ground_and_solve()
        room = [sig.symbol.arguments[1] for sig 
                in self.ctl.symbolic_atoms.by_signature("is_in_room", 3)
                if sig.symbol.arguments[2] == Number(time) and
                sig.symbol.arguments[0] == String(agent)]
        assert(len(room) == 1), self.debug_model()
        return str(room[0]).strip("\"")
    
    def get_all_rooms(self) -> List[str]:
        # get all "is in room" and "goto" values 
        self.ground_and_solve()
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
        self.ctl.add(f'go_to("{location}", {self.curr_tp}).')
        self.inc_curr_tp()
        self.ground_and_solve()

    def ask(self, person : str, question : str, options: List[str]) -> str:
        # issue ask and r() options, get reply at T+1
        for opt in options:
            self.ctl.add(f"r({opt}).")
        self.ctl.add(f'ask("{person}", "{question}", {self.curr_tp}).')
        self.inc_curr_tp()
        self.ground_and_solve()
        
    

def main():
    c = Context()
    # NL command:
    c.ctl.add('is_in_room("robot", "start_loc", 0).')
    # c.ctl.add("init_states", [], 'is_in_room("Arjun", "office", 0).')
    # c.ctl.add("")
    # generated LLM code:
    loc1 = c.get_current_location()
    print("loc1:", loc1)
    c.ctl.cleanup()
    tp1 = c.curr_tp
    print("tp1:", tp1)
    # c.ctl.add('id(1).')
    # c.ctl.ground(c.parts)
    c.go_to("office")
    # # c.ctl.ground()
    tp2 = c.curr_tp
    print("tp2:", tp2)
    loc2 = c.get_current_location()
    print("loc2:",loc2)
    
    with c.ctl.solve(yield_=True) as hnd:
            for i,m in enumerate(hnd):
                print("Answer: ",i)
                print(m)
            print(hnd.get())
    
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
