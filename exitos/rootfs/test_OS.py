# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:55:52 2025

@author: Belen
"""
import download_state
import post_state
import OS_lab as OS_lab

Loads = [ 592.45634747, 592.49635485, 591.85913229, 587.32300037, 586.73134253, 658.20264316, 764.18414501, 892.49415179,1059.20503953,1139.24205145,1047.32752325, 911.3889703 , 830.37283932, 810.47591246, 725.17024209, 655.69050001, 633.23086019, 656.17916226, 674.2013454 , 613.44323685, 630.28952584, 623.30421259, 622.07467228, 615.39167492]
PV = [5.94394677e+00,1.24269512e+00,9.34323393e-02,9.85697932e-02,4.45894808e-01,1.50230271e+02,7.28816702e+02,1.38984333e+03,1.98963365e+03,2.41026367e+03,2.53855949e+03,2.54364465e+03,1.89310506e+03,1.97221394e+03,1.47734965e+03,1.33669594e+03,4.51399602e+02,1.49279818e+02,3.94424950e+01,2.60363683e+01,1.23473593e+00,8.13592035e-02,2.45826099e-01,4.26342606e-01]

print("Lectura de variables")
bat_master = download_state.download_state("sensor.sunvec_capacidad_bateria_master")/100
bat_slave = download_state.download_state("sensor.sunvec_capacidad_bateria_slave_1")/100
print("Bateria Master:")
print(bat_master)
print("Bateria Slave:")
print(bat_slave)

optimizer = OS_lab.OS_lab(building_dem=Loads,solar_prod=PV,bat_inicial_master=bat_master,bat_inicial_slave=bat_slave)

print("Optimizando")
BESS = optimizer.optimize()
print("Optimizacion Finalizada")

#Calculem la flexivilitat de la solucio trobada.
#### Bateria
import BESS_lab as BESS_lab

SoC = bat_master 
bateria_master = BESS_lab.BESS_lab(SoC,debug=False) #SoC inicial en tant per 1
SoC = bat_slave 
bateria_slave = BESS_lab.BESS_lab(SoC,debug=False) #SoC inicial en tant per 1

#Calculem el power min i max que podrem posar /treure de la bateria segons el metode de control seleccionat i forcasts
c_master=[]
c_slave=[]
for i in range(0,24):
    c_master.append(bateria_master.control(method=BESS[i],load = Loads[i], production = PV[i]))
    c_slave.append(bateria_master.control(method=BESS[i+24],load = Loads[i], production = PV[i]))
    #positivo: potencia de carga; negativo: potencia de descarga

print("Simulando Bateria 1")
#donat el control Fem la simulacio.
kwh_master, SoC_master = bateria_master.simula(c_master)
print("Simulando Bateria 2")
kwh_slave, SoC_slave = bateria_slave.simula(c_slave)
#kwh negativo: extraido de la red; positivo: inyectado
print("Simulacion Finalizada")

print("Publicando Estados:")
post_state.post_state("input_select.modo_optimo_bateria_master",BESS[0:24])
print("Control Master Publicado: ", BESS[0:24])
post_state.post_state("input_select.modo_optimo_bateria_slave",BESS[25])
print("Control Slave Publicado: ", BESS[25])
post_state.post_state("input_number.potencia_bateria_master",kwh_master[1])
print("Potencia Master Publicada: ", kwh_master[1])
post_state.post_state("input_number.potencia_bateria_slave",kwh_slave[1])
print("Potencia Slave Publicada: ", kwh_slave[1])
post_state.post_state("input_number.soc_bateria_master",SoC_master[1]*100)
print("SoC Master Publicado: ", SoC_master[1]*100)
post_state.post_state("input_number.soc_bateria_slave",SoC_slave[1]*100)
print("SoC Slave Publicado: ", SoC_slave[1]*100)

#donada la simulacio calculem flexivilitat que tindrem
# dt_BESS_master, dt_plus_BESS_master, dt_minus_BESS_master = bateria_master.flex(kwh_master, SoC_master)
# dt_BESS_slave, dt_plus_BESS_slave, dt_minus_BESS_slave = bateria_slave.flex(kwh_slave, SoC_slave)

##visualitzem (positiu bateria consumeix de xarxa - Negatiu injecta)
# import matplotlib.pyplot as plt
# # plt.figure()
# # plt.plot(dt_BESS, label='Consum Bateria',  color='k')
# # plt.plot(dt_minus_BESS+dt_BESS, label='Consum minim',  color='b', linestyle='-.')
# # plt.plot(dt_plus_BESS+dt_BESS, label='Consum maxim',   color='r', linestyle='-.')
# # plt.legend()
# # plt.show()
# plt.figure()
# plt.plot(kwh_master, label='Consum Bateria Master',  color='k')
# plt.plot(kwh_slave, label='Consum Bateria Slave',  color='b', linestyle='-.')
# plt.legend()
# plt.show()
