n = 200
Str = str(n)
import numpy as np
for _ in range(n):
    Str += "\n{} {} {} {}".format(np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand())

with open("butterfly_v2.edg", "w") as f:
    f.write(Str)