import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


plt.style.use('ggplot')
mpl.rcParams['figure.figsize']= [15, 9]


S = np.load("./data/1590832874-1593424874.npy")

plt.plot(S[:, :1], lw=1.5)
plt.xlabel('time')
plt.ylabel('index level')
plt.savefig("treand.png")
plt.show()