from enum import IntEnum, unique

class priority(IntEnum):
    low                                =    1  # Low priority, background messages
    normal                             =    5  # Normal priority, standard messages
    high                               =   10  # High priority, only for critical messages
def get_name(val):
        print(f"Getting name for value {val}")

        for cls in (priority):
            print(f"Trying to get name for {val} from {cls}")   
            try:
                return f"{cls(val).name}"
            except Exception:
                pass
        print(f"Could not get name for value {val}, returning string representation")
        return str(val)

#a = priority(5)
#print()
#print(str(get_name(a)))  

def priority_to_string(value: int) -> str:
    try:
        return f"{priority(value).__class__.__name__}.{priority(value).name}"
    except ValueError:
        return f"priority.unknown({value})"

a = priority_to_string(5)
print(a)
print(type(a))
