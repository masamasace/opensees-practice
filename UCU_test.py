'''
# Description: This script is used to perform a cyclic simple shear test on a soil element using OpenSeesPy.
# Reference: https://github.com/zhuminjie/OpenSeesPyDoc/blob/master/pyExamples/PM4Sand_Cyc_Cal.py
'''

############ Import libraries ############
import openseespy.opensees as op
import matplotlib.pyplot as plt
import pandas as pd

############ Define parameters ############

# Element size
height = 1.0 
width = 1.0

confining_pressure = -200

rho = 1.42
D_r = 0.5  
G_o = 476.0
h_po = 0.53
Den = 2000
e_max = 0.8
e_min = 0.5
e_ini = e_max - (e_max - e_min) * D_r

# Element parameters
thickness = 1.0
fBulk = 2.2e6
fDen = 1.0e3
perm_1 = 1.0e-9
perm_2 = 1.0e-9
alpha = 1.0e-5

# Rayleigh damping parameters
damp = 0.02
omega1 = 0.2
omega2 = 20.0
a1 = 2.0 * damp / (omega1 + omega2)
a0 = a1 * omega1 * omega2

# Define model builder
op.wipe()
op.model('basic', '-ndm', 2, '-ndf', 3)

# Define nodes
op.node(1, 0, 0)
op.node(2, width, 0)
op.node(3, width, height)
op.node(4, 0, height)

# Define boundary conditions
op.fix(1, 1, 1, 1)
op.fix(2, 1, 1, 1)
op.fix(3, 0, 0, 1)
op.fix(4, 0, 0, 1)
op.equalDOF(3, 4, 1, 2)

# Define material
op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den)

# Define single quad element
op.element('SSPquadUP', 1, 1, 2, 3, 4, 1, thickness, fBulk, fDen, perm_1, perm_2, e_ini, alpha)

# Create recorder to store element stress and strain
op.recorder('Node', '-file', 'Cycdisp.txt', '-time', '-node', 1, 2, 3, 4, '-dof', 1, 2, 'disp')
# op.recorder('Node', '-file', 'CycPP.txt', '-time', '-node', 1, 2, 3, 4, '-dof', 3, 'vel')
op.recorder('Element', '-file', 'CycStrain.txt', '-time', '-ele', 1, 'strain')
op.recorder('Element', '-file', 'CycStress.txt', '-time', '-ele', 1, 'stress')

op.constraints('Transformation')
op.test('NormDispIncr', 1.0e-5, 100, 1)
op.algorithm('Newton')
op.numberer('RCM')
op.system('FullGeneral')
op.integrator('Newmark', 5.0/6.0, 4.0/9.0)
op.rayleigh(a1, a0, 0.0, 0.0) 
op.analysis('Transient')

pNode = confining_pressure / 2

op.timeSeries('Path', 1, '-values', 0, 1, 1, '-time', 0, 100, 1.0e10)
op.pattern('Plain', 1, 1, '-fact', 1.0)
op.load(3, 0, pNode, 0)
op.load(4, 0, pNode, 0)
op.updateMaterialStage('-material', 1, '-stage', 0)

op.analyze(100, 1)

v_disp = op.nodeDisp(3, 2)
op.timeSeries('Path', 2, '-values', 1, 1, 1, '-time', 0, 100, 1.0e10)
op.pattern('Plain', 2, 2, '-fact', 1.0)
op.sp(3, 2, v_disp)
op.sp(4, 2, v_disp)

# Make the element to be undrained
for i in range(4):
    op.remove("sp", i+1, 3)

op.analyze(100, 1)

op.updateMaterialStage('-material', 1, '-stage', 1)
op.setParameter('-val', 0, '-ele', 1, 'FirstCall', "1")

op.analyze(100, 1)

op.wipe()



# Define shear wave load
# op.timeSeries('Trig', 1, 0, 5, shear_wave_period)
# op.pattern('Plain', 2, 1)
# op.load(3, shear_wave_amplitude, 0.0)
# op.load(4, shear_wave_amplitude, 0.0)

# Perform analysis
# op.analyze(1000, 0.01)

df_disp = pd.read_csv('Cycdisp.txt', sep='\s+', header=None)
df_stress = pd.read_csv('CycStress.txt', sep='\s+', header=None)
df_strain = pd.read_csv('CycStrain.txt', sep='\s+', header=None)

print(df_disp)
print(df_stress)
print(df_strain)
