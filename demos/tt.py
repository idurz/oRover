import oroverlib as orover

class priority(IntEnum):
    low                                =    1  # Low priority, background messages
    normal                             =    5  # Normal priority, standard messages
    high                               =   10  # High priority, only for critical messages


def get_name(self, val) -> str:
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
            try:
                return f"{cls(val).__class__.__name__}.{cls(val).name}"
            except ValueError:
                pass
        return f"{cls(val).__class__.__name__}.unknown({val})"

s = "sensor_ultrasonic_front"

if not s in orover.origin._member_names_:
    print(f"config.ini section hcsr04, is not defined as known sensor in origin")

print("done")
#        sensorid = p.get_name(sensorinfo[0])

