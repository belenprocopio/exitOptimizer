# -*- coding: utf-8 -*-
import numpy as np

class BESS_lab:
    """
    Model de les 1 bateries
    """
    def __init__(self, bat_ini = 0.5, debug=False):
        """
        Constructor per defecte de l'objecte.
        
                bat_ini - l'estat de la bateria a l'inici de la simulacio en tant per 1.
        """
        #parametres de la bateria i el carregador
        self.efficency = 0.95 # 95% eficencia de la bateria. El que es perd amb la carrega, pero no en descarrega
        
        self.max_power_discharge = -7.5 # el que decarrega hora max kW
        self.max_power_charge = 7.5 # el que carrega hora max kW

        self.bat_max = 5.8*2 #11.6 #Maxim en KW, 5.8 kW por modulo
        self.bat_min = self.bat_max*0.1 #Minim en KW
        
        self.bat_inicial = self.bat_max * bat_ini # estat inicial en kW
        
        self.temps_simulacio = 1 # en hores, es el pas de la simulacio. 1h = 1, 15 min =  1/4,....
        
        self.debug=debug
        
    def simula(self, power = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]):
        """
        Simula el comportament de la bateria al llarg d'un dia a nivell horari.
        
        power - El que fara la bateria. (Positiu carrega negatiu descarrega)
        
        """
        # Ens passen el % que volem que tingui la nostra bateria. 
        #ho convertim a % que hem de carregar o descarregar

        estat = self.bat_inicial# en kWh
        SoC=[]#estat de carrega en %
        kwh=[]#estat de carrega en kwh
        
        #estat de carrega inicial ens marcara la flexivilitat de la primera hora
        SoC.append(estat / self.bat_max)
        
        for i in range(0,len(power)):#per cada "hora" mirem que farra la bateria
            if self.debug:
                print('-----')
                
            if power[i] > 0:
                #carregarem
                pow_corr = min(power[i], self.max_power_charge) * self.temps_simulacio #energia maxima que absorbirem de xarxa
                estatnext = estat + (pow_corr * self.efficency) #Estat de carrega que estariem si suposem que podem fer el que diuen.
                estatnext = min(estatnext,self.bat_max)#comprovem que no passem del maxim o el % indicat
                
                kwh.append((estat - estatnext)/ self.efficency / self.temps_simulacio)#quedara en negatiu el que hem xupat de xarxa estatnext sera mes gran sempre perque hem carregat.
                SoC.append(estatnext / self.bat_max)
                
                if self.debug:
                    print("Kwh emmagatzemats inicials:"+str(estat))
                    print("KWh emmagatzemats seguent:"+str(estatnext))
                    print("SoC:")
                    print(SoC)
                    print("Power Real en kWh:")
                    print(kwh)

                estat  = estatnext
                
            elif power[i] < 0:
                #descarregarem
                pow_corr = max(power[i], self.max_power_discharge) * self.temps_simulacio #energia maxima que injectarem de xarxa
                estatnext = estat + pow_corr #el que injectem a la xarxa si suposem que podem fer el que diuen.
                estatnext = max(estatnext,self.bat_min)#comprovem que no sortim dels minims i maxims
                
                kwh.append((estat - estatnext) / self.temps_simulacio)#quedara en positiu el que hem injectat a xarxa. next sempre es mes petit que l'anterior
                SoC.append(estatnext/self.bat_max)
                if self.debug:
                    print("Kwh emmagatzemats inicials:"+str(estat))
                    print("KWh emmagatzemats seguent:"+str(estatnext))
                    print("SoC:")
                    print(SoC)
                    print("Power Real en kWh:")
                    print(kwh)
                estat = estatnext
                
            else:
                #no fa res
                if self.debug:
                    print("Bateria inactiva")
                kwh.append(0)
                SoC.append(estat/self.bat_max)

        return np.array(kwh) , np.array(SoC)
        #kwh que dona o rep cada h, Soc en kWh
        
    def control(self, method = 'charge', load = 3, production = 2):
        if method == 'charge':
            power = self.max_power_charge
        elif method == 'discharge':
            power = self.max_power_discharge
        elif method == 'solar':
            power = production - load
        elif method == 'off':
            power = 0
        else:
            power = 0
        return power 
    
    # def flex(self, kwh, SoC):
    #     dt = kwh
    #     dt_plus =[]
    #     dt_minus =[]
    #     for i in range(len(kwh)):
    #         if SoC[i] < 1: 
    #             dt_plus.append( self.max_power_charge - kwh[i] )
    #         else:
    #             dt_plus.append( 0)
            
    #         if SoC[i] > 0.1: #puc descarregar
    #             dt_minus.append(self.max_power_discharge - kwh[i])
    #         else:
    #             dt_minus.append( 0 )

    #     return dt, dt_plus, dt_minus
            
