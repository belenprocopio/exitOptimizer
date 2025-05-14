# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from BESS_lab import BESS_lab as Bess

class OS_lab():
    
    def __init__(self, 
                 elec_prices=[0.133, 0.126, 0.128, 0.141, 0.147, 0.148, 0.155, 0.156, 0.158, 0.152, 0.147, 0.148, 0.144, 0.141, 0.139, 0.136, 0.134, 0.137, 0.143, 0.152, 0.157, 0.164, 0.159, 0.156],
                 venta_electr = [0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054,0.054],
                 building_dem=[1380.3333333333333,839.3076923076923,853.5833333333334,1623.8333333333333,846.2307692307693,918.9166666666666,1539.0,2118.714285714286,1464.0833333333333,438.0,417.2857142857143,438.5833333333333,408.5,1390.3846153846155,439.3333333333333,441.72727272727275,720.0666666666667,1643.6363636363637,2205.5833333333335,1630.0714285714287,1878.6363636363637,3408.8333333333335,2823.5,1976.6363636363637],
                 solar_prod=[0.0,0.0,0.0,0.0,0.0,0.0,0.09090909090909091,26.5,74.5,205.54545454545453,285.14285714285717,481.25,711.8,506.38461538461536,379.0,181.36363636363637,135.53333333333333,26.272727272727273,0.08333333333333333,0.0,0.0,0.0,0.0,0.0],
                 bat_inicial = 0.28,
                 num_bat=4,
                 consums=pd.DataFrame(),
                 excedents=pd.DataFrame(),
                 coef=[1,1,1,1,1],
                 price_consum=[1,1,1,1,1],
                 price_excedent=[1,1,1,1,1],
                 debug=False
                 ):
        
        """
        Constructor de l'objecte, es passen per parametre tots els attributs necessaris per realitzar la simulacio i es guarden dins l'objecte.
        """
        #if debug will se prints
        self.debug = debug
        
        # solar production
        self.sp = np.array(solar_prod)
        
        # Consumptions edificis Tots sumats!
        self.ec = np.array(building_dem)
        
        #consumos individuales
        self.consums = consums
        
        #excedentes individuales
        self.excedents = excedents
        
        #coeficients reparto
        self.coef = coef
        
        #precios de consumo
        self.price_consum = price_consum
        
        #precios de excedente
        self.price_excedent = price_excedent
        
        #preu de l'electricitat 
        self.prices = np.array(elec_prices)
        
        #preus de venta d'electricitat
        self.prices_venta = np.array(venta_electr)
        
        #estat inicial bateries
        self.bat_ini = bat_inicial
        
        #numero de baterias
        self.num_bat = num_bat
                
        #preparem les bateries
        self.Bess_bat = Bess(bat_ini=self.bat_ini,num_bat= self.num_bat, debug=self.debug)
        
        #algorisme solver
        self.alg='SA' # 'PSO' = particle swarm; 'SA' = simulated anealing; 'DE' = Diferential Evolution; 'least_squares' = least_squares;
        
       
    def cost(self,x):
        """
        Funcio de cost completa on s'optimitza totes les variables possibles.
        """
        ### BESS - Bateria electrica controlem que fa per percentatge
        #x[0] fins a x[23]  --> Es el mode de operacio de la bateria.
        x = list(np.around(np.array(x),0))
        
        powers=[]
        m=[]
        for i in range(0,24):
            #Traduim de la particula al metode desitjat.
            if x[i] == 0:
                m='off'
            if x[i] == 1:
                m='discharge'
            if x[i] == 2:
                m='solar'
            # if x[i] == 3:
            #     m='charge'
            
            powers.append( self.Bess_bat.control(method=m,load = self.ec[i], production = self.sp[i]))
            
        
        #simulem bateria.
        kwh_Bess, SoC_Bess = self.Bess_bat.simula(powers[0:])
        
        #calculem que gastem /injectem a xarxa
        valans_energetic = self.ec - (self.sp  + kwh_Bess)
        
        injectat =valans_energetic.copy()
        injectat[injectat>0]=0 #treiem positius
        injectat=abs(injectat) #valor absolut
        
        consumit = valans_energetic.copy()
        consumit[consumit<0]=0
        
        #comptabilitzem els kw dins la bateria. A preu de venda mig diari. els inicials negatius els finals positius.
        bats = (SoC_Bess[-1] - self.bat_ini) * self.Bess_bat.bat_max * self.prices_venta.mean()
        
        #funcio de cost
        preu = sum(sum(np.outer(consumit,self.coef) * self.price_consum)) - sum(sum(np.outer(injectat,self.coef) * self.price_excedent)) + bats
        return preu
    
    
    def optimize(self):
        """
        Funcio que engega la optimitzacio corresponent. i retorna la millor comanda que s'ha trobat per retornar a l'ESB 
        """
        
        if self.alg=='PSO':
            import pyswarms as ps
            particules=24# Create bounds
            max_bound = [2]*24
            min_bound = [0]*24
            bounds = (min_bound, max_bound)
            
            # Initialize swarm
            options = {'c1': 2, 'c2': 2, 'w':0.4}
            
            # Call instance of PSO with bounds argument
            optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=particules, options=options, bounds=bounds)
            def f(x):
                x = list(np.around(np.array(x),0))
                nparticles=x.shape[0]
                preus_solucions=[self.cost(x[i]) for i in range(nparticles)]
                return np.array(preus_solucions)
            cost, x = optimizer.optimize(f, iters=10000)
            x=np.array(x).round()
            
        elif self.alg=='SA':
            from scipy.optimize import dual_annealing
            max_bound = [2]*24
            min_bound = [0]*24
            res=dual_annealing(self.cost, bounds=list(zip(min_bound,max_bound)), no_local_search = False)
            x=res.x
            x=np.array(res.x).round()
            
        elif self.alg=='DE':
            from scipy.optimize import differential_evolution
            max_bound = [2]*24
            min_bound = [0]*24
            
            def f(x):
                x = list(np.around(np.array(x),0))
                return self.cost(np.array(x).round())
            res=differential_evolution(f, bounds=list(zip(min_bound,max_bound)))
            x=np.array(res.x).round()
                       
        elif self.alg=='least_squares':
            from scipy.optimize import least_squares
            max_bound = [2]*24
            min_bound = [0]*24
            
            res=least_squares(self.cost,x0=np.array(max_bound)/2, bounds=(min_bound,max_bound))
            x=res.x
        
        #Posem be el retorn, repetint les variables que calgui segons index
        BESS = []
        m =[]
        for i in range(0,24):
            #Traduim de la particula al metode desitjat.
            if x[i] == 0:
                m='off'
            if x[i] == 1:
                m='discharge'
            if x[i] == 2:
                m='solar'
            # if x[i] == 3:
            #     m='charge'
            BESS.append(m)
        
        
        return np.array(BESS)