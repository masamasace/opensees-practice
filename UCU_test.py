import openseespy.opensees as op
import numpy as np
import matplotlib.pyplot as plt

# Define parameters
height = 1.0 
width = 1.0

confining_pressure = 100 * 10 ** 3

shear_wave_period = 10
shear_wave_amplitude = 10

rho = 2000
D_r = 0.5  
G_o = 12500000
h_po = 0.3
Den = 2000
e_max = 0.8
e_min = 0.5
e_ini = e_max - (e_max - e_min) * D_r

# Define model builder
op.wipe()
op.model('basic', '-ndm', 2, '-ndf', 2)

# Define nodes
op.node(1, 0, 0)
op.node(2, width, 0)
op.node(3, width, height)
op.node(4, 0, height)

# Define boundary conditions
op.fix(1, 1, 1)
op.fix(2, 1, 1)
op.fix(3, 0, 0)
op.fix(4, 0, 0)
op.equalDOF(3, 4, 1, 2)

# Define material
op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den)

# Define single quad element
op.element('SSPquad', 1, 1, 2, 3, 4, 1, 1.0, 2.2e6, 1.0, 1e-9, 1e-9, e_ini, 1.0e-5)

# Define shear wave load
# op.timeSeries('Trig', 1, 0, 5, shear_wave_period)
# op.pattern('Plain', 2, 1)
# op.load(3, shear_wave_amplitude, 0.0)
# op.load(4, shear_wave_amplitude, 0.0)


# Define analysis procedure
op.system('BandGeneral')
op.numberer('Plain')
op.constraints('Plain')
op.integrator('Newmark', 0.5, 0.25)
op.algorithm('Newton')
op.analysis('Transient')

# Define recorders to store stress and strain
op.recorder('Element', '-file', 'stress_strain.out', '-time', '-ele', 1, 'stress')
op.recorder('Element', '-file', 'strain_strain.out', '-time', '-ele', 1, 'strain')

# Perform analysis
op.analyze(1000, 0.01)

# Read the recorded data
time = []
stress = []
strain = []

with open('stress_strain.out', 'r') as f:
    for line in f:
        data = line.split()
        time.append(float(data[0]))
        stress.append(float(data[1]))

with open('strain_strain.out', 'r') as f:
    for line in f:
        data = line.split()
        strain.append(float(data[1]))

# Plot the stress-strain graph
fig, ax = plt.subplots(ncols=3, figsize=(15, 5))

ax[0].plot(strain, stress)
ax[1].plot(time, stress)
ax[2].plot(time, strain)

ax[0].set_xlabel('Strain')
ax[0].set_ylabel('Stress')
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Stress')
ax[2].set_xlabel('Time')
ax[2].set_ylabel('Strain')

# do not close the plot window
plt.show()
