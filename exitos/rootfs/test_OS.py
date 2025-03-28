# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:55:52 2025

@author: Belen
"""
"""
import pandas as pd

print("Leyendo datos")
df_potencia_ct = pd.read_csv("datos\potencia_ct.csv", delimiter=',')
df_solar1 = pd.read_csv("datos\paneles_master.csv", delimiter=',')
df_solar2 = pd.read_csv("datos\paneles_slave.csv", delimiter=',')

df_potencia_ct["last_changed"] = pd.to_datetime(df_potencia_ct["last_changed"])
df_solar1["last_changed"] = pd.to_datetime(df_solar1["last_changed"])
df_solar2["last_changed"] = pd.to_datetime(df_solar2["last_changed"])



df_potencia_ct_resampled = df_potencia_ct.set_index("last_changed").resample("1h").first().reset_index()
df_solar1_resampled = df_solar1.set_index("last_changed").resample("1h").first().reset_index().fillna(0)
df_solar2_resampled = df_solar2.set_index("last_changed").resample("1h").first().reset_index().fillna(0)

df_potencia_ct_resampled["state"] = pd.to_numeric(df_potencia_ct_resampled["state"],errors='coerce')
df_solar1_resampled["state"] = pd.to_numeric(df_solar1_resampled["state"],errors='coerce')
df_solar2_resampled["state"] = pd.to_numeric(df_solar2_resampled["state"],errors='coerce')
"""

import OS_lab as OS_lab

Loads = [ 592.45634747, 592.49635485, 591.85913229, 587.32300037, 586.73134253, 658.20264316, 764.18414501, 892.49415179,1059.20503953,1139.24205145,1047.32752325, 911.3889703 , 830.37283932, 810.47591246, 725.17024209, 655.69050001, 633.23086019, 656.17916226, 674.2013454 , 613.44323685, 630.28952584, 623.30421259, 622.07467228, 615.39167492]
PV=[5.94394677e+00,1.24269512e+00,9.34323393e-02,9.85697932e-02,4.45894808e-01,1.50230271e+02,7.28816702e+02,1.38984333e+03,1.98963365e+03,2.41026367e+03,2.53855949e+03,2.54364465e+03,1.89310506e+03,1.97221394e+03,1.47734965e+03,1.33669594e+03,4.51399602e+02,1.49279818e+02,3.94424950e+01,2.60363683e+01,1.23473593e+00,8.13592035e-02,2.45826099e-01,4.26342606e-01]


"""
Loads = df_potencia_ct_resampled["state"].to_list()
PV = df_solar1_resampled["state"].to_list() + df_solar2_resampled["state"].to_list()
"""
bat_master = 0.28
bat_slave = 0.26


"""
Loads: consumo del edificio (kW)
PV: producción solar (kW)
bat: SoC inicial de la bateria
"""

"""
max_len = 24
if len(Loads) > max_len:
    Loads = Loads[:max_len]
if len(PV) > max_len:
    PV = PV[:max_len]
while len(PV) < len(Loads):
    PV.append(0)

Loads = [-x for x in Loads] #Cambio de signo
#W a kW
Loads = [x/1000 for x in Loads]
PV = [x/1000 for x in PV]
"""

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