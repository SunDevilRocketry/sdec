# List of hardware to be controlled
engine_hardware = ["sol1", "sol2", "valve1", "valve2", "stepper1", "stepper2"]
# List of commands to send
engine_commands = ["ignite", 
                   "abort", 
                   "telreq", 
                   "pfpurge", 
                   "fillchill", 
                   "standby", 
                   "hotfire",
                   "getstate",
                   "stophotfire",
                   "stoppurge",
                   "loxpurge",
                   "datalog"]

# List of allowed variants of on or off
allowed_on_off = ["on", "On", "oN", "ON", "1",
                  "off", "Off", "OFf", "OfF", "ofF", "oFf", "OFF", "0"]


# Syntax error function for parse_CSV() can use to throw syntax errors
def syntax_error(line_no, message):
    print(f"Syntax Error <{message}> at line: {line_no} while parsing")
    exit(-1)

# Parse a given CSV file following the sample sheet rules
# Place each time and command in a list which is appended to the sequence list
# Returns: sequence_commands: <List>
def parse_CSV(file):
    sequence_commands = []
    line_no = 0

    with open(file, "r") as f:
        first_line = f.readline() # Consume first line 
        for line in f:
            start_char = line[0]
            if start_char != ",":
                if start_char.isdigit():
                    line = line.split(",")
                    time = line[0]
                    time = float(time)
                    command = line[1].lower()
                    new_line = [time, command]
                    sequence_commands.append(new_line)
                else:
                    syntax_error(line_no, "Unexpected Character: Commands start with digits")
    
    return sequence_commands

# Perform syntax checking on the parsed data
# Returns: syntax_pass: <bool>, command_no: <int>, message: <string>
def syntax_checking(sequence_list):
    command_no = 1
    prev_time = -1

    # Make sure first command given is the initial "0, sequencing ON"
    first_pair = sequence_list[0]
    if first_pair[0] != 0:
        return False, 0, "Sequencing ON command not at time 0"
    first_command = first_pair[1].split(" ")
    if first_command[0] != "sequencing":
        return False, 0, "First command not sequecning"
    if first_command[1] != "on":
        return False, 0, "First command prompt not ON"
    sequence_list = sequence_list[1:]

    for pair in sequence_list:
        time = pair[0]

        # Make sure the time sequence is strictly increasing or equal to
        if time < prev_time:
            return False, command_no, "Non-Increasing Time Sequence"
        
        # Determine if command is a hardware access or a command
        command = pair[1].split(" ")
        hardware_or_command = command[0]
        on_or_off = command[1]

        if hardware_or_command in engine_hardware:
            # Command is to control hardware
            if on_or_off not in allowed_on_off or on_or_off not in allowed_on_off:
                # ON or OFF prompt not provided
                return False, command_no, "Hardware Access requires an ON or OFF"
        elif hardware_or_command in engine_commands:
            # Command is to send an engine command
            if on_or_off != "on":
                # ON prompt not provided
                return False, command_no, "Command send requires an ON"
        else:
            # Command does not exist
            return False, command_no, f"Hardware or Command '{hardware_or_command}' does not exist"

        command_no += 1
        prev_time = time

    # No syntax problems found
    return True, 0, ""

# Format the parsed list into a dict for serialization 
def format_as_dict(sequence_list):
    sequence_dict = {}

    for pair in sequence_list:
        time = pair[0]
        command = pair[1]

        if time in sequence_dict.keys():
            sequence_dict[time].append(command)
        else:
            sequence_dict[time] = [command]

    return sequence_dict

# Print the sequence dict with formatting 
def print_sequence(sequence_dict):
    times = sequence_dict.keys()
    for time in times:
        commands = sequence_dict[time]
        for command in commands:
            command = command.split(" ")
            hardware_or_command = command[0]
            on_or_off = command[1]

            print(str(time) + ": " + hardware_or_command + " " + on_or_off)

def main():
    sequence_list = parse_CSV("Liquid Avionics Sequencing Document - Sheet1.csv")
    print(sequence_list)
    syntax_result = syntax_checking(sequence_list)
    if (not syntax_result[0]):
        print(f"Syntax Error: <{syntax_result[2]}> at command number: {syntax_result[1]}")
        exit(-1)
    else:
        print("Syntax checking passed")
        sequence_dict = format_as_dict(sequence_list)
        print_sequence(sequence_dict)

if __name__ == "__main__":
    main()