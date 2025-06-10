# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:55:52 2025

@author: Belen
"""
import pandas as pd

print("Leyendo datos")

# Función para generar nombres de columnas tipo Excel: A, B, ..., Z, AA, AB, ...
def excel_column_name(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

# Generar las primeras 42 columnas alternas empezando por C (índice 3 en Excel)
columnas_consum = [excel_column_name(i) for i in range(3, 3 + 2*42, 2)]
# Generar las primeras 42 columnas alternas empezando por D (índice 4 en Excel)
columnas_excedent = [excel_column_name(i) for i in range(4, 4 + 2*42, 2)]

# Leer consumo y excedente de los participantes
df_consum = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Consum i Excedents",
    usecols=",".join(columnas_consum),
    skiprows=1,
    nrows=24
).fillna(0)

df_excedent = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Consum i Excedents",
    usecols=",".join(columnas_excedent),
    skiprows=1,
    nrows=24
).fillna(0)

df_preu_consum = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Dades",
    usecols='K',
    skiprows=1,
    nrows=42
).fillna(0)

df_preu_excedent = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Dades",
    usecols='N',
    skiprows=1,
    nrows=42
).fillna(0)

df_coef = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Dades",
    usecols='I',
    skiprows=1,
    nrows=42
).fillna(0)


# # Sumar filas
# df_consum = df_consum.sum(axis=1)

df_solar = pd.read_excel(
    "Consum_Data.xlsx",
    sheet_name="Generacio",
    usecols="C",
    # skiprows=1,
    nrows=24
).fillna(0)

print('Datos Leidos')


import OS_lab as OS_lab
from elec_price import elec_price

import download_state
import post_state
import time

"""
Loads = [ 592.45634747, 592.49635485, 591.85913229, 587.32300037, 586.73134253, 658.20264316, 764.18414501, 892.49415179,1059.20503953,1139.24205145,1047.32752325, 911.3889703 , 830.37283932, 810.47591246, 725.17024209, 655.69050001, 633.23086019, 656.17916226, 674.2013454 , 613.44323685, 630.28952584, 623.30421259, 622.07467228, 615.39167492]
PV=[5.94394677e+00,1.24269512e+00,9.34323393e-02,9.85697932e-02,4.45894808e-01,1.50230271e+02,7.28816702e+02,1.38984333e+03,1.98963365e+03,2.41026367e+03,2.53855949e+03,2.54364465e+03,1.89310506e+03,1.97221394e+03,1.47734965e+03,1.33669594e+03,4.51399602e+02,1.49279818e+02,3.94424950e+01,2.60363683e+01,1.23473593e+00,8.13592035e-02,2.45826099e-01,4.26342606e-01]
bat = 0.5
"""

Loads = list(df_consum.sum(axis=1))
PV = df_solar["Generacio"].to_list()

"""
Loads: consumo del edificio (kW)
PV: producción solar (kW)
bat: SoC inicial de la bateria
"""

print("Lectura de variables de HA")

#Carga inicial de las baterias
#Lectura desde Home Assistant
bat_1 = download_state.download_state("sensor.sunvec_capacidad_bateria_master")/100
bat_2 = download_state.download_state("sensor.sunvec_capacidad_bateria_slave_1")/100

num_bat = 2
bat_ini = (bat_1+bat_2)/num_bat

print("Bateria 1:")
print(bat_1)
print("Bateria 2:")
print(bat_2)

prices = elec_price()
print("Precios:")
print(prices)

print("Variables listas")

optimizer = OS_lab.OS_lab(building_dem=Loads,
                          consums=df_consum,
                          excedents = df_excedent, 
                          coef=df_coef.values.flatten(),
                          price_consum=df_preu_consum.values.flatten(),
                          price_excedent=df_preu_excedent.values.flatten(),
                          solar_prod=PV,
                          num_bat=num_bat,
                          bat_inicial = bat_ini)

print("Optimizando")
BESS = optimizer.optimize()
print("Optimizacion Finalizada")

#Calculem la flexivilitat de la solucio trobada.
#### Bateria
import BESS_lab as BESS_lab


bateria = BESS_lab.BESS_lab(bat_ini=bat_ini, num_bat = num_bat,debug=False)

#Calculem el power min i max que podrem posar /treure de la bateria segons el metode de control seleccionat i forcasts
c=[]
for i in range(0,24):
    c.append(bateria.control(method=BESS[i],load = Loads[i], production = PV[i]))
    #positivo: potencia de carga; negativo: potencia de descarga

print("Simulando Bateria")
#donat el control Fem la simulacio.
kwh, SoC = bateria.simula(c)
print("Simulacion Finalizada")
#negativo: kwh de carga; positivo: kwh de descarga


wh = [round(num*1000) for num in kwh]
SoC = [round(num*100) for num in SoC]

print("Control optimo: ", BESS)

print("Publicando Estados:")
for i in range(0,24):
    #Control bateria
    # if BESS[i] == 'off':
    #     m="Stop force charge&discharge"
    # if BESS[i] == 'discharge':
    #     m="Force discharge"
    # if BESS[i] == 'solar':
    #     m="Force charge"
    # post_state.post_state("select.sunvec_control_manual_baterias",m)
    # print("select.sunvec_control_manual_baterias Publicado: ", m)

    post_state.post_state("input_text.modo_optimo_bateria_master",BESS[i])
    print("Control Bateria 1 Valor ",i," Publicado: ", BESS[i])
    post_state.post_state("input_text.modo_optimo_bateria_slave",BESS[i])
    print("Control Bateria 2 Valor ",i," Publicado: ", BESS[i])
    post_state.post_state("input_number.prediccion_potencia_bateria_master",wh[i]/num_bat)
    print("Potencia Bateria 1 Valor ",i," Publicada: ", wh[i]/num_bat)
    post_state.post_state("input_number.prediccion_potencia_bateria_slave",wh[i]/num_bat)
    print("Potencia Bateria 2 Valor ",i," Publicada: ", wh[i]/num_bat)
    post_state.post_state("input_number.prediccion_soc_bateria_master",SoC[i])
    print("SoC Bateria 1 Valor ",i," Publicado: ", SoC[i])
    post_state.post_state("input_number.prediccion_soc_bateria_slave",SoC[i])
    print("SoC Bateria 2 Valor ",i," Publicado: ", SoC[i])
    time.sleep(3600)

post_state.post_state("input_text.modo_optimo_bateria_master",'off')
print("Estado Final Control Bateria 1 Publicado: ", 'off')
post_state.post_state("input_text.modo_optimo_bateria_slave",'off')
print("Estado Final Control Bateria 2 Publicado: ", 'off')

print("Todos los estados publicados")
