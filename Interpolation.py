class Interpolation:

    @staticmethod
    def interpolate(a, b, p):
        a *= 1.0-p
        b *= p
        return a+b

    @staticmethod
    def interpolateTuple(a, b, p):
        if(len(a) != len(b)):
            raise ValueError(f"Tuples '{a}' and '{b}' are not the same size")

        values = []
        for i in range(len(a)):
            values.append(Interpolation.interpolate(a[i], b[i], p))

        return tuple(values)
