import pandas as pd
import matplotlib.pyplot as plt

df= pd.read_table('luminosity.txt', sep = ',')

plt.plot(df['Time'],df['Intensity'],marker='o')
plt.xlabel('Clock Time (Hr)')
plt.ylabel('Luminous Intensity micromol.m^-2.s^-1')
plt.suptitle('Luminous intensity vs Time of day')
plt.savefig('luminosity.jpg')
plt.show()

