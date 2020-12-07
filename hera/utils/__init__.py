from unum import Unum

def andClause(excludeFields=[], **kwargs):

    L = []
    for key, value in kwargs.items():
        if key in excludeFields:
            continue

        if isinstance(value, list):
            conditionStr = "%s in %s"
        elif isinstance(value, str):
            conditionStr = "%s == '%s'"
        elif isinstance(value, dict):
            conditionStr = "%s " + value['operator'] + " %s"
            value = value['value']
        else:
            conditionStr = "%s == %s"

        L.append(conditionStr % (key, value))

    return " and ".join(L)


<<<<<<< HEAD
tonumber = lambda x,theunit: x.asNumber(theunit) if isinstance(x,Unum) else x
tounit   = lambda x,theunit: x.asUnit(theunit) if isinstance(x,Unum) else x*theunit

toMeteorologicalAngle = lambda mathematical_angle: (270-mathematical_angle) if ((270-mathematical_angle) >= 0) else (630-mathematical_angle)
toMathematicalAngle  = toMeteorologicalAngle

=======
>>>>>>> 7fbf20536c81c54cd69d1745f88bbcb264158e82

#############

