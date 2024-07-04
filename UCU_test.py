import openseespy.opensees as op
import numpy as np
import matplotlib.pyplot as plt

# Define model builder
op.wipe()
op.model('basic', '-ndm', 2, '-ndf', 2)

# Define parameters
height = 10.0  # height of the soil column (m)
num_elem = 10  # number of elements
elem_height = height / num_elem  # height of each element
width = 1.0  # width of the column (m)
shear_wave_frequency = 1.0  # frequency of the shear wave (Hz)
shear_wave_amplitude = 1  # amplitude of the shear wave (m)

# Define nodes
op.node(1, 0, 0)
op.node(2, width, 0)
op.node(3, width, elem_height)
op.node(4, 0, elem_height)



# Define boundary conditions
op.fix(1, 1, 1)
op.fix(2, 1, 1)
op.fix(3, 0, 0)
op.fix(4, 0, 0)

# Define nonlinear material
rho = 2000
D_r = 0.5  # Relative density
G_o = 12500000
h_po = 0.3
Den = 2000


op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den)

# Define single quad element
op.element('quad', 1, 1, 2, 3, 4, 1.0, 'PlaneStrain', 1, 0.0, rho, 0.0, -9.81)

# Define gravity load
op.timeSeries('Linear', 1)
op.pattern('Plain', 1, 1)
gravity_load = -rho * 9.81 * width * height / 4
vertical_confining_force = 100 * 1000 * width * height / 2
horizontal_confining_force = 100 * 1000 * width * height / 2

op.load(1, horizontal_confining_force, gravity_load - vertical_confining_force)
op.load(2, -horizontal_confining_force, gravity_load - vertical_confining_force)
op.load(3, -horizontal_confining_force, gravity_load + vertical_confining_force)
op.load(4, horizontal_confining_force, gravity_load + vertical_confining_force)


# Define shear wave load
shear_wave_ts_tag = 2

op.timeSeries('Trig', shear_wave_ts_tag, 0, 1000, 10)
op.pattern('Plain', 2, shear_wave_ts_tag)
op.load(3, shear_wave_amplitude, 0.0)
op.load(4, shear_wave_amplitude, 0.0)


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
op.analyze(10000, 0.01)

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
