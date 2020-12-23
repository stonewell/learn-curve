import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(1,120,120)
y = (2*10**-5)**2 + ((0.001)/(x))**2

plt.plot(x, y)
plt.show()
