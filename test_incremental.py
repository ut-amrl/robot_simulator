from ast import cmpop
from clingo import *
from observer import Observer
"""
    start_loc = get_current_loc()
    go_to("Arjun's office")
    response = ask("Arjun", "ready to head out?", ["yes", "no", "maybe"])
    go_to(start_loc)
    say("Arjun said: " + response)
"""
    
def main():
    ob = Observer()
    ctl = Control()
    ctl.register_observer(ob)
    
    ctl.load("robot_test.lp")
    ctl.add('is_in_room("robot", "start_loc", 0).')

    e0 = Function("id", [Number(0)])
    e1 = Function("id", [Number(1)])
    e2 = Function("id", [Number(2)])
    e3 = Function("id", [Number(3)])
    e4 = Function("id", [Number(4)])
    e5 = Function("id", [Number(5)])
    
    ctl.ground([("base", []), ("time", [])])
    ctl.assign_external(e0, True)
    ctl.assign_external(e1, True)
    # ctl.release_external(e2)
    # ctl.release_external(e3)
    
    

    
    # ctl.cleanup()
    # ctl.ground()
    # ctl.assign_external(e2, False)
    # ctl.assign_external(e3, False)
    # ctl.release_external(e2)
    # ctl.release_external(e3)
    # ctl.cleanup()
    # # ctl.add('go_to("office", 1).')
    # # ctl.ground()
    # ctl.solve(on_model=lambda m: print("\nAnswer: {}".format(m)))
    
    # ctl.add("time", [], 'go_to("office", 1).')
    # ctl.ground([("time", [Number(1)])])
    # ctl.cleanup()
    # mod = None
    # with ctl.solve(yield_=True) as hnd:
    #     # print(hnd.get())
    #     for i,m in enumerate(hnd):
    #         mod = m
    #         mod.context.add_clause(['go_to("office", 1).'])
    #         print("Answer: {}".format(mod))
    #         # with ctl.backend() as backend:
    #         #     atm_a = backend.add_atom(Function("go_to", [String("office"), Number(1)]))
    #         #     backend.add_rule([atm_a])

    #         # ctl.assign_external(e0, True)
    #         # ctl.assign_external(e1, True)
    #         # ctl.ground([("base", [])])
    #         ctl.assign_external(e2, True)
    #         ctl.assign_external(e3, True)
    #         mod.context.wait()
            
    
    # mod = None
    # with ctl.solve(yield_=True) as hnd:
    #     # print(hnd.get())
    #     for i,m in enumerate(hnd):
    #         mod = m
            
            # for i,m in enumerate(hnd):
            #     print("Answer: ",i)
            #     print(m)
            # print(hnd.get())
            
    ctl.solve(on_model=lambda m: print("\nAnswer2: {}".format(m)))
    print(ob.rules, ob.terms, ob.atoms)
    # ctl.assign_external(e2, True)
    # ctl.assign_external(e3, True)
            
if __name__ == "__main__":
    main()