__version__ = '2.1.3'

import os
import json


import logging.config


with open(os.path.join(os.path.dirname(__file__),'logging','heraLogging.config'),'r') as logconfile:
     log_conf_str = logconfile.read().replace("\n","")
     log_conf = json.loads(log_conf_str.replace("{herapath}",os.path.dirname(__file__)))

EXECUTION = 15
logging.addLevelName(EXECUTION, 'EXECUTION')


def execution(self, message, *args, **kws):
    self.log(EXECUTION, message, *args, **kws)

logging.Logger.execution = execution
logging.config.dictConfig(log_conf)


from .toolkit import ToolkitHome
toolkitHome =ToolkitHome()

########################## Units for the model.
from unum import Unum,NameConflictError
from unum.units import *


from .utils import toMathematicalAngle,toMeteorologicalAngle,tonumber,tounit

try:
    atm = Unum.unit('atm',Pa*101325.,'atm = 101325 pascal')
    mmHg  = Unum.unit('mmHg',atm/760.,'mmHg = 1 torr')
    torr  = Unum.unit('torr',atm/760.,'torr = 1 mmHg')

    dyne  = Unum.unit('dyne',1e-5*N,'dyne')
    poise = Unum.unit('poise',g/cm/s,'poise')
    cpoise = Unum.unit('cpoise',poise/10.,'centipoise')
except NameConflictError:
    pass

"""

2.1.3
-----
    - Few corrections of the documentation and some minor bugs. 

2.1.2
-----
   - Fixing some bugs in the previous version 
   - Added printing to formatted text of an agent. 

2.1.1
-----


buildings:
     - refactoring the code

OF-LSM:
     - fixed small bug in reading points

Topography:
     - Removed extra code    
    
Experiment: 
     -   Fixed the dynamic load of the experiment.  

2.1.0
-----
     
    - GIS
        Topography: 
                - Add height. Adds the topography height to a regular data. 
                              The topography is interpolated from pandas (with xarray).   
              
    - openFOAM : 
            NavierStokes
                - Adding Canopy profile.
                
            LSM:
                - Updating Ustar/Hmix 
                - Fixed some bugs in the OF-LSM reading files.
                - Changed getSource to makeSource
               
    - datalayer:
        - project to specify the logger name.         
        - adding 'dict' data format to store dict as a resource. 
    
2.0.2
-----
    - Examples gallery for the risk assessment  
    - Fixing the pvServerRun 

2.0.1
-----
    - Example for the toolkits raster 
    - fixed bug in the get concentration of the LSM
    - Updating the documentaiton 

2.0.0
-----
    - Fixing the commit
    - Changing the structure of the toolkits. 
    - Fixing the imports to be lighter
    - Some other changes to make the risk assessment procedure work.  
    - Updating the AgentsHome according to the existing agents description
    - changed wind_speed to horizontal_wind_speed in the turbulence calculator. 

 1.1.3
------
   - Updates of the documentation. 
   - Minor refactoring of the utils. 

 1.1.2
------
  - Changes to the intepolations in the simulations module. 
  - updated documentations. 
   

 1.1.1
------ 

    - Changes to the  command lines. 
    - Rearranging the meteorology. 


 1.0.0
 -----
    - Introduced tools. 
        - The GIS tools work  
    - Project classes are equipped with a logger. 

 This version consists a structural change that introduces concept of Tools. 
 
 A tool is a set of library functions that is designed to handle a single type of data. 
 Many tools also include a capability to search for public data automatically. 
 
 The change is cosmetic, but also includes several new concepts in tools such as datasource. 
 A datasource is the name of data that will be used by default by the tool. For examplt the BNTL data 
 is the default datasource of the mesasurements.GIS.topography tool. In this 
 example, the default datasource is stored in the public database. 
 
 0.7.0
 -----
  - Adding the riskassessment package. 
  - Adding the simulations/gaussian package. 
  - adding the simulation/evaporation package. 

 0.6.1
 -----
  - Fixing the simulations.interpolations package. 
  - Renanimg interpolation->spatialInterpolations.  
  
 0.6.0
 -----
  - adding tonumber,tounum and tometeorological/to mathematical functions to the utils. 

 0.5.1
 -----
 CampbellBinary parser and datalayer fixed.

 0.5.0
 -----
 Changed the meteorology structure(datalayer and presentaionlayer)

 0.4.1
 -----
 With demography in GIS

 0.4.0
 -----
 Added features to the turbulence calculator.
 Added options to the db documents search.

 0.3.0
 -----
 Changed the datalayer.analysis to datalayer.cache.
 Added more documentation.

 0.2.2
 -----
 Turbulence calculator working with sampling window None.

 0.2.1
 -----
 More turbulence calculator fix

 0.2.0
 -----
 Turbulence calculator fix

 0.1.1
 -----
 Removed the necessity to have a public DB

 0.1.0
 -----
 getData() from datalayer returns list of data.


 0.0.2
 -----
 
 LSM - * Tiding up the datalayer a bit 
       * LagrangianReader - changing the order of the x and y coordinates



"""
