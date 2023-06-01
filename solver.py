from clingo import Control, ast
from clingo.solving import Model
from clingo.symbol import Function, String, Number
from typing import List 
import clingo
from observer import Observer
import random 

class Context:

    def __init__(self, robot_cmds_file = "robot.lp", init_state = [], timeout=10):
        self.ctl = Control()
        self.timeout=timeout
        self.ctl.load(robot_cmds_file)
        # self.observer = Observer()
        # self.ctl.register_observer(self.observer)
        
        # self.parts = [("init_states", []),("rules", []), ("nl_commands", [])]
        self.ctl.add(f"#const timeout = {timeout}.")
        # for i in range(timeout):
        # self.ctl.add(f"#external id.")
            # self.ctl.add(f"id({i}) :- ext{i}.")
        # self.ctl.assign_external(Function(f"id"), True)
        self.curr_tp = 0
        self.curr_robot_loc = "start_loc"
        self.all_rooms = ["start_loc"]
        self.curr_reply = ""
        self.init_state = init_state
        for atom in init_state:
            self.ctl.add(atom)
        
    def inc_curr_tp(self):
        self.curr_tp += 1
        # self.ctl.add(f"id({self.curr_tp}) :- ext{self.curr_tp}.")

    def ground_and_solve(self):
        self.ctl.ground()
        self.ctl.solve(on_model=lambda m: print("\nAnswer: {}".format(m)))
        return self.debug_model()

        
    def debug_model(self):
        model = []
        with self.ctl.solve(yield_=True) as hnd:
            for i,m in enumerate(hnd):
                # print(m)
                model.append(str(m))
        print(hnd.get())
        return model
            
    def get_current_location(self) -> str:
        # get robot location at max time (from is_in_room)
        return self.curr_robot_loc

    
    def get_all_rooms(self) -> List[str]:
        # get all "is in room" and "goto" values 
        return self.all_rooms
    
    
    def is_in_room(self, obj : str) -> bool:
        # check if is in the room at curr time step
        curr_loc = self.get_current_location()
        for atom in self.init_state:
            if f'is_in_room("{obj}", "{curr_loc}",' in atom:
                return True
        return False

        
    ## actions: ground after each action
    
    ## get most curr response
    def say(self, message : str) -> None:
        # get most current reply
        self.ctl.add(f'say("{message}", {self.curr_tp}).')
        
    def go_to(self, location : str) -> None:
        # issue goto
        self.all_rooms.append(location)
        self.ctl.add(f'go_to("{location}", {self.curr_tp}).')
        self.inc_curr_tp() 
        self.curr_robot_loc = location

    def ask(self, person : str, question : str, options: List[str]) -> str:
        # issue ask and r() options, get reply at T+1
        opt = random.sample(options, k=1)[0]
        
        self.curr_reply = opt
        self.ctl.add(f"r({opt}).")
        self.ctl.add(f'ask("{person}", "{question}", {self.curr_tp}).')
        return self.curr_reply
"""
Note:
- once grounded, you can't change that chunk of code
- adding to solver just adds dead branch to search (need custom propagator)
- custom observer is best for getting
"""    

def main():
    """
    start_loc = get_current_loc()
    go_to("Arjun's office")
    response = ask("Arjun", "ready to head out?", ["yes", "no", "maybe"])
    go_to(start_loc)
    say("Arjun said: " + response)
    """
  
    init_state = ['is_in_room("robot", "start_loc", 0).',
                    'is_in_room("Arjun", "office", 0).']
    c = Context(timeout=3, init_state=init_state)
    
    start_loc = c.get_current_location()
    c.go_to("office")
    assert(c.is_in_room("Arjun"))
    response = c.ask("Arjun", "ready to head out?", ["yes", "no"])
    c.go_to(start_loc)
    c.say("Arjun said: " + response)
    

    c.ctl.add(f':- not is_in_room("robot", "start_loc", {c.timeout}).')
    c.ctl.add(f':- not replied("Arjun", _, _).')
    c.ground_and_solve()
    
    init_state = ['is_in_room("robot", "start_loc", 0).',
                    'is_in_room("mug", "living_room", 0).']
    c = Context(timeout=3, init_state=init_state)
    start_loc = c.get_current_location()
    c.go_to("living_room")
    mug_found = c.is_in_room("mug")
    c.go_to(start_loc)
    if mug_found:
        c.say("There is a mug in the living room")
    else:
        c.say("There is no mug in the living room")
        
    c.ctl.add(':- not say("There is a mug in the living room", _).')
    c.ctl.add(f':- not is_in_room("robot", "start_loc", {c.timeout}).')
    c.ground_and_solve()

if __name__=="__main__":
    main()
    

