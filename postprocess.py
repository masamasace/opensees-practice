'''
Draw animation of stress and strain in the element by using matplotlib
'''

import matplotlib.pyplot as plt
from matplotlib import animation, rc
import numpy as np  
import pandas as pd
from matplotlib.patches import Polygon

df_disp = pd.read_csv('Cycdisp.txt', sep='\s+', header=None)
df_stress = pd.read_csv('CycStress.txt', sep='\s+', header=None)
df_strain = pd.read_csv('CycStrain.txt', sep='\s+', header=None)

fig = plt.figure()

# box animation
ax1 = fig.add_subplot(2, 1, 1)

initial_vertices = np.array([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])
polygon_ax1 = Polygon(initial_vertices, closed=True, edgecolor='k', facecolor='b', alpha=1)
ax1.add_patch(polygon_ax1)
magnification_ratio = 20.0
df_stress["mean"] = -(df_stress[1] + df_stress[2]) / 2
max_mean_stress = df_stress["mean"].max()

# text annotation
txt_ax1 = ax1.text(-2, 0, "", fontsize=8, ha='left', va='bottom')


ax1.set_xlim(-0.5, 1.5)
ax1.set_ylim(-0.5, 1.5)
ax1.set_aspect('equal')
ax1.axis('off')

ax2 = fig.add_subplot(2, 2, 3)
ax2.plot(df_strain[3], df_stress[3], linewidth=0.5, color='k')
point_ax2 = ax2.plot(df_strain[3][0], df_stress[3][0], 'ro')[0]
ax2.set_xlabel(r'Shear strain, $\gamma$')
ax2.set_ylabel(r'Shear stress, $ \tau $')

ax3 = fig.add_subplot(2, 2, 4)
ax3.plot(-(df_stress[1]+df_stress[2])/2, df_stress[3], linewidth=0.5, color='k')
point_ax3 = ax3.plot(df_stress["mean"][0], df_stress[3][0], 'ro')[0]
ax3.set_xlabel(r"Mean effective stress, $p'$")
ax3.set_ylabel(r'Shear stress, $ \tau $')

fig.subplots_adjust(wspace=0.35)

def update(i):
    
    shear_increment = df_strain[3][i] * magnification_ratio
    sheared_vertices = initial_vertices.copy()
    sheared_vertices[2][0] += shear_increment
    sheared_vertices[3][0] += shear_increment
    polygon_ax1.set_xy(sheared_vertices)
    
    # change polygon color based on the mean effective stress
    prs_mean_effetive_stress = df_stress["mean"][i]
    prs_ratio = (max_mean_stress - prs_mean_effetive_stress) / max_mean_stress 
    if prs_ratio < 0:
        prs_ratio = 0
    
    polygon_ax1.set_facecolor((1-prs_ratio, 1-prs_ratio, 1))
    

    annotaiton_text = f"Step: {i}\n" + \
    f"Shear strain: {df_strain[3][i]:<8.4f}\n" + \
    f"Shear stress: {df_stress[3][i]:<6.2f}\n" + \
    f"Mean stress: {prs_mean_effetive_stress:<6.2f}"
        
    txt_ax1.set_text(annotaiton_text)
    
    point_ax2.set_data([df_strain[3][i]], [df_stress[3][i]])
    point_ax3.set_data([prs_mean_effetive_stress], [df_stress[3][i]])
    
    return txt_ax1, polygon_ax1, point_ax2, point_ax3

frame_num = np.arange(0, len(df_disp[3]), 5)

anim = animation.FuncAnimation(fig, update, frames=frame_num, interval=5, blit=False)

rc('animation', html='jshtml')
# save animation as mp4
anim.save('CycElement.mp4', writer='ffmpeg', fps=30)