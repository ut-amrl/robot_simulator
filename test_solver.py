from solver import Context

def test_time():
    c = Context()
    # NL command:
    c.ctl.add("init_states", [], 'is_in_room("robot", "start_loc", 0).')
    c.ctl.add("init_states", [], 'is_in_room("Arjun", "office", 0).')
    c.ctl.add("")
    # generated LLM code:
    loc1 = c.get_current_location()
    tp1 = c.curr_tp
    c.go_to("Arjun's office")
    loc2 = c.get_current_location()
    tp2 = c.curr_tp
    assert(loc1 == "start_loc"), loc1
    assert(loc2 == "Arjun's office"), loc2
    assert(tp1 == 0), tp1
    assert(tp2 == 1), tp2
    
