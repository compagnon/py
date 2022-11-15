# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# initialize the parameters for the normal
# distribution, namely mean and std.
# deviation

# defining the mean
mu = 0.5
# defining the standard deviation
sigma = 0.1

# The random module uses the seed value as a base
# to generate a random number. If seed value is not
# present, it takes the system’s current time.
np.random.seed(0)

# define the x co-ordinates
X = np.random.normal(mu, sigma, (395, 1))

# define the y co-ordinates
Y = np.random.normal(mu * 2, sigma * 3, (395, 1))

# plot a graph
plt.scatter(X, Y, color = 'g')
plt.show()


# en torch
import torch
x = torch.rand(5, 3)
print(x)