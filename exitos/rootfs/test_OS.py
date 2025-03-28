# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 11:54:44 2024

@author: Mi PC
"""

import OS_lab as OS_lab

Loads = [ 592.45634747, 592.49635485, 591.85913229, 587.32300037, 586.73134253, 658.20264316, 764.18414501, 892.49415179,1059.20503953,1139.24205145,1047.32752325, 911.3889703 , 830.37283932, 810.47591246, 725.17024209, 655.69050001, 633.23086019, 656.17916226, 674.2013454 , 613.44323685, 630.28952584, 623.30421259, 622.07467228, 615.39167492]
PV=[5.94394677e+00,1.24269512e+00,9.34323393e-02,9.85697932e-02,4.45894808e-01,1.50230271e+02,7.28816702e+02,1.38984333e+03,1.98963365e+03,2.41026367e+03,2.53855949e+03,2.54364465e+03,1.89310506e+03,1.97221394e+03,1.47734965e+03,1.33669594e+03,4.51399602e+02,1.49279818e+02,3.94424950e+01,2.60363683e+01,1.23473593e+00,8.13592035e-02,2.45826099e-01,4.26342606e-01]
bat = 0.5

optimizer = OS_lab.OS_lab(building_dem=Loads,solar_prod=PV,bat_inicial=bat)


BESS = optimizer.optimize()


#Calculem la flexivilitat de la solucio trobada.
#### Bateria
import BESS_lab as BESS_lab

SoC = bat 
bateria = BESS_lab.BESS_lab(SoC,debug=False) #SoC inicial en tant per 1

#Calculem el power min i max que podrem posar /treure de la bateria segons el metode de control seleccionat i forcasts
c=[]
for i in range(0,24):
    c.append(bateria.control(method=BESS[i],load = Loads[i], production = PV[i]))

#donat el control Fem la simulacio.
kwh, SoC = bateria.simula(c)

#donada la simulacio calculem flexivilitat que tindrem
# dt_BESS, dt_plus_BESS, dt_minus_BESS = bateria.flex(kwh, SoC)

# ##visualitzem (positiu bateria consumeix de xarxa - Negatiu injecta)
# import matplotlib.pyplot as plt
# plt.figure()
# plt.plot(dt_BESS, label='Consum Bateria',  color='k')
# plt.plot(dt_minus_BESS+dt_BESS, label='Consum minim',  color='b', linestyle='-.')
# plt.plot(dt_plus_BESS+dt_BESS, label='Consum maxim',   color='r', linestyle='-.')
# plt.legend()
# plt.show()
