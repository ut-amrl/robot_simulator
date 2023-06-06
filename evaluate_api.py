import sys 
import json 
from solver import Context
c = Context()

def substitute_function_calls(program: str):
    # convert function call
    program = program.replace("get_current_location(", "c.get_current_location(")
    program = program.replace("get_all_rooms(", "c.get_all_rooms(")
    program = program.replace("is_in_room(", "c.is_in_room(")
    program = program.replace("say(", "c.say(")
    program = program.replace("go_to(", "c.go_to(")
    program = program.replace("ask(", "c.ask(")

    return program 

def setup_eval(instruction: dict):
    init_state = instruction["init_state"]
    timeout = instruction["timeout"]
    rooms = instruction["rooms"]
    c = Context(timeout=timeout, init_state=init_state)
    c.all_rooms.extend(rooms)
    return c

def wrapup_eval(c: Context, instructions: list[str], is_sat: bool, local_variables: dict):
    for instruction in instructions:
        condition = instruction["condition"]
        variables = instruction["variables"]
        local_vars = []
        for var in variables:
            local_vars.append(local_variables[var])
        condition = condition.format(*local_vars)
        c.ctl.add(condition)
    (model, is_success) = c.ground_and_solve()

    if is_sat:
        assert(str(is_success) ==  "SAT"), (model, str(is_success))
    else:
        assert(str(is_success) == "UNSAT"), (model, str(is_success))

def execute(program_data: dict):
    program = program_data["program"]
    prompt = program_data["prompt"]
    setup_eval_instruction = program_data["setup_eval_instruction"]
    wrap_up_eval_instruction = program_data["wrap_up_eval_instruction"]
    is_sat = program_data["is_sat"]

    try:
        program = substitute_function_calls(program)
        c = setup_eval(setup_eval_instruction)
        
        exec(program)

        wrapup_eval(c, wrap_up_eval_instruction, is_sat, locals())

    except Exception as e:
        print("program failed: ", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("you need to provide more than two arguments")
    
    filename = sys.argv[1]
    with open(filename, "r") as f:
        program_data = json.load(f)
    
    execute(program_data)
