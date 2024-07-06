'''
# Description: This script is used to perform a cyclic simple shear test on a soil element using OpenSeesPy.
# Reference: https://github.com/zhuminjie/OpenSeesPyDoc/blob/master/pyExamples/PM4Sand_Cyc_Cal.py
'''

############ Import libraries ############
import openseespy.opensees as op
import matplotlib.pyplot as plt
import pandas as pd

############ Define functions ############
def extract_stress_strain(stress, strain, disp, flag=False):
    
    prs_shear_stress = stress[2]
    prs_mean_stress = (stress[0] + stress[1]) / 2
    prs_shear_strain = strain[2]
    prs_hol_dsip = disp
    
    if flag:
        print('tau:', "{:<6.2f}".format(prs_shear_stress), 
            'sigma:', "{:<6.2f}".format(prs_mean_stress), 
            'gamma:', "{:<8.4f}".format(prs_shear_strain))
    
    return (prs_shear_stress, prs_mean_stress, prs_shear_strain, prs_hol_dsip)
    

############ Define parameters ############

# Element size
height = 1.0
width = 1.0

# Material parameters
sigma_c = -100

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

# Shear loading parameters
shear_wave_period = 0.1

# Flags to export results
flag_export_txt_under_load = False

############ Define model ############

# Wipe a remaining model. This should be done before creating a new model.
op.wipe()

# Define model with number of dimensions and degrees of freedom
# ndf is set automatically to ndm*(ndm+1)/2 according to the manual
op.model('basic', '-ndm', 2, '-ndf', 3)

# Define nodes
# Square domain with 4 nodes
op.node(1, 0, 0)
op.node(2, width, 0)
op.node(3, width, height)
op.node(4, 0, height)

# Define boundary conditions
# Fix nodes 1 and 2 in any direction and fix nodes 3 and 4 in rotation
op.fix(1, 1, 1, 1)
op.fix(2, 1, 1, 1)
op.fix(3, 0, 0, 1)
op.fix(4, 0, 0, 1)

# multi-point constraint between nodes 3 and 4 to ensure equal horizontal and vertical displacements
op.equalDOF(3, 4, 1, 2)


############ Define materials and elements ############
# some unwritten parameters are set to default values
op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den)

# Define single quad element
op.element('SSPquadUP', 1, 1, 2, 3, 4, 1, thickness,
           fBulk, fDen, perm_1, perm_2, e_ini, alpha)


############ Define recorders ############
# Create recorder to store element stress and strain
# To record pore presure, refer `-dof 3` and `vel` in the recorder command
op.recorder('Node', '-file', 'Cycdisp.txt', '-time',
            '-node', 1, 2, 3, 4, '-dof', 1, 2, 'disp')
op.recorder('Node', '-file', 'CycPP.txt', '-time',
            '-node', 1, 2, 3, 4, '-dof', 3, 'vel')
op.recorder('Element', '-file', 'CycStrain.txt', '-time', '-ele', 1, 'strain')
op.recorder('Element', '-file', 'CycStress.txt', '-time', '-ele', 1, 'stress')


############ Define analysis ############
# Still need to study the following commands
op.constraints('Transformation')

# Define convergence condtions
# last argument is PrintFlag to change how to display the convergence result in each step
op.test('NormDispIncr', 1.0e-5, 100, 0)
op.algorithm('Newton')
op.numberer('RCM')

# `FullGeneral` is not recommended for large models. Better to use `BandGeneral` instead.
op.system('FullGeneral')

# Define integrator
# According to official documentation, there are some common choices for the integrator:
op.integrator('Newmark', 0.5, 0.25)
op.rayleigh(a1, a0, 0.0, 0.0)
op.analysis('Transient')

############ Apply initial static load ############

op.timeSeries('Path', 1, '-values', 0, 1, 1, '-time', 0, 100, 1.0e10)
op.pattern('Plain', 1, 1, '-fact', 1.0)
op.load(3, 0, sigma_c / 2, 0)
op.load(4, 0, sigma_c / 2, 0)

# Change its constitutive model to Linear Elastic one
op.updateMaterialStage('-material', 1, '-stage', 0)

op.analyze(100, 1)

############ Make specimen undrained and wait for pore pressure to stabilize ############

v_disp = op.nodeDisp(3, 2)
op.timeSeries('Path', 2, '-values', 1, 1, 1, '-time', 100, 1000, 1.0e10)
op.pattern('Plain', 2, 2, '-fact', 1.0)
op.sp(3, 2, v_disp)
op.sp(4, 2, v_disp)

# Make the element to be undrained
for i in range(4):
    op.remove("sp", i+1, 3)

op.analyze(100, 1)

# Change its constitutive model to PM4Sand
op.updateMaterialStage('-material', 1, '-stage', 1)

# The following command is needed to initialize the PM4Sand model
op.setParameter('-val', 0, '-ele', 1, 'FirstCall', "1")

op.analyze(100, 1)

op.setParameter('-val', 0.3, '-ele', 1, 'poissonRatio', '1')

############ Perform cyclic simple shear test ############

thres_hol_disp = 0.03
limiting_hol_disp = 1.1 * thres_hol_disp
prs_num_cycle = 0.25
target_num_cycle = 10
increment_strain = 0.0001
CSR = 0.2

while (prs_num_cycle <= target_num_cycle):

    # impose 1/4 cycle
    prs_hol_dsip = op.nodeDisp(3, 1)
    prs_time = op.getTime()
    required_steps = limiting_hol_disp / increment_strain
    time_change = prs_time + required_steps

    op.timeSeries('Path', 3, '-values', prs_hol_dsip, limiting_hol_disp, limiting_hol_disp,
                  '-time', prs_time, time_change, 1.0e10, '-factor', 1.0)
    op.pattern('Plain', 3, 3, '-fact', 1.0)
    op.sp(3, 1, 1.0)

    prs_shear_stress, prs_mean_stress, prs_shear_strain, prs_hol_dsip = extract_stress_strain(
        op.eleResponse(1, 'stress'), op.eleResponse(1, 'strain'),  op.nodeDisp(3, 1), flag_export_txt_under_load)

    while prs_shear_stress <= -CSR * sigma_c:
        op.analyze(1, 1.0)
        
        prs_shear_stress, prs_mean_stress, prs_shear_strain, prs_hol_dsip = extract_stress_strain(
            op.eleResponse(1, 'stress'), op.eleResponse(1, 'strain'),  op.nodeDisp(3, 1))
        
        if prs_hol_dsip >= thres_hol_disp:
            break
    
    print('Number of cycles:', prs_num_cycle)
    
    # impose 1/2 cycle from maximum shear stress to minimum shear stress
    prs_num_cycle = prs_num_cycle + 0.5
    prs_hol_dsip = op.nodeDisp(3, 1)
    prs_time = op.getTime()
    op.remove('loadPattern', 3)
    op.remove('timeSeries', 3)
    op.remove('sp', 3, 1)

    required_steps = (limiting_hol_disp+prs_hol_dsip)/increment_strain
    time_change = prs_time + required_steps
    op.timeSeries('Path', 3, '-values', prs_hol_dsip, -1.0*limiting_hol_disp, -1.0 *
                  limiting_hol_disp, '-time', prs_time, time_change, 1.0e10, '-factor', 1.0)
    op.pattern('Plain', 3, 3)
    op.sp(3, 1, 1.0)
    
    while prs_shear_stress > CSR * sigma_c or prs_hol_dsip <= -thres_hol_disp:
        op.analyze(1, 1.0)
        
        prs_shear_stress, prs_mean_stress, prs_shear_strain, prs_hol_dsip = extract_stress_strain(
            op.eleResponse(1, 'stress'), op.eleResponse(1, 'strain'),  op.nodeDisp(3, 1), flag_export_txt_under_load)
        
        if prs_hol_dsip <= -thres_hol_disp:
            break
        
    print('Number of cycles:', prs_num_cycle)
    
    # impose 1/4 cycle
    prs_num_cycle = prs_num_cycle + 0.25
    prs_hol_dsip = op.nodeDisp(3, 1)
    prs_time = op.getTime()
    op.remove('loadPattern', 3)
    op.remove('timeSeries', 3)
    op.remove('sp', 3, 1)

    required_steps = (limiting_hol_disp+prs_hol_dsip)/increment_strain
    op.timeSeries('Path', 3, '-values', prs_hol_dsip, limiting_hol_disp, limiting_hol_disp,
                  '-time', prs_time, time_change, 1.0e10, '-factor', 1.0)
    op.pattern('Plain', 3, 3, '-fact', 1.0)
    op.sp(3, 1, 1.0)
    
    while prs_shear_stress <= 0.0:
        op.analyze(1, 1.0)
        
        prs_shear_stress, prs_mean_stress, prs_shear_strain, prs_hol_dsip = extract_stress_strain(
            op.eleResponse(1, 'stress'), op.eleResponse(1, 'strain'),  op.nodeDisp(3, 1), flag_export_txt_under_load)
        
        if prs_hol_dsip >= thres_hol_disp:
            break
    
    print('Number of cycles:', prs_num_cycle)
        
    prs_num_cycle = prs_num_cycle + 0.25
    op.remove('loadPattern', 3)
    op.remove('timeSeries', 3)

op.wipe()

df_disp = pd.read_csv('Cycdisp.txt', sep='\s+', header=None)
df_stress = pd.read_csv('CycStress.txt', sep='\s+', header=None)
df_strain = pd.read_csv('CycStrain.txt', sep='\s+', header=None)

fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].plot(df_strain[3], df_stress[3])
ax[1].plot(-(df_stress[1]+df_stress[2])/2, df_stress[3])

plt.show()
