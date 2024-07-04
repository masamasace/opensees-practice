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
shear_wave_amplitude = 0.01  # amplitude of the shear wave (m)

# Define material properties
rho = 2000.0  # density (kg/m^3)
E = 1e7  # Young's modulus (Pa)
nu = 0.3  # Poisson's ratio
G = E / (2 * (1 + nu))  # Shear modulus
su = 100.0  # undrained shear strength (Pa)
friction_angle = 30.0  # friction angle in degrees
phase_transform_angle = 30.0  # phase transformation angle in degrees
ref_shear_modulus = 1.0e4  # reference shear modulus
ref_bulk_modulus = 1.0e5  # reference bulk modulus
cohesion = 50.0  # cohesion
peak_shear_strain = 0.1  # peak shear strain
ref_press = 101.0  # reference pressure
press_depend_coeff = 0.5  # pressure dependence coefficient
contraction_param1 = 0.1  # contraction parameter 1
dilation_param1 = 0.1  # dilation parameter 1
dilation_param2 = 0.1  # dilation parameter 2
liquefaction_param1 = 0.1  # liquefaction parameter 1
liquefaction_param2 = 0.1  # liquefaction parameter 2
liquefaction_param4 = 0.1  # liquefaction parameter 4
number_of_yield_surfaces = 20  # number of yield surfaces
e = 0.6  # void ratio
vol_limit1 = 0.9  # volumetric limit 1
vol_limit2 = 0.02  # volumetric limit 2
vol_limit3 = 0.7  # volumetric limit 3
atmospheric_pressure = 101.0  # atmospheric pressure

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
D_r = 0.5  # Relative density
G_o = 125.0
h_po = 0.3
Den = 2000.0
P_atm = 101.0
h_o = 0.1
e_max = 0.8
e_min = 0.5
n_b = 0.5
n_d = 0.1
A_do = 0.8
z_max = 1.0
c_z = 0.4
c_e = 0.3
phi_cv = 33.0
g_degr = 2.0
c_dr = 0.5
c_kaf = 0.4
Q_bolt = 2.0
R_bolt = 1.0
m_par = 0.05
F_sed = 0.3
p_sed = 1.0

op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den, P_atm, h_o, e_max, e_min, n_b, n_d, A_do, z_max, c_z, c_e, phi_cv, nu, g_degr, c_dr, c_kaf, Q_bolt, R_bolt, m_par, F_sed, p_sed)

# Define single quad element
op.element('quad', 1, 1, 2, 3, 4, 1.0, 'PlaneStrain', 1, 0.0, rho, 0.0, -9.81)

# Define gravity load
op.timeSeries('Linear', 1)
op.pattern('Plain', 1, 1)
op.load(1, 0.0, -rho * 9.81 * width * height / 4)
op.load(2, 0.0, -rho * 9.81 * width * height / 4)
op.load(3, 0.0, -rho * 9.81 * width * height / 4)
op.load(4, 0.0, -rho * 9.81 * width * height / 4)

# Define shear wave load
shear_wave_ts_tag = 2
op.timeSeries('Trig', shear_wave_ts_tag, shear_wave_amplitude, shear_wave_frequency, 1.0 / shear_wave_frequency)
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
plt.figure()
plt.plot(time, strain, label='Strain')
# plt.plot(time, stress, label='Stress')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('Stress and Strain Time History')
plt.legend()
plt.show()
