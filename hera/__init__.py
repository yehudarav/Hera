__version__ = '0.3.0'






import sys
## Load modules if it is python 3.
version = sys.version_info[0]
if version==3:
    from .simulations import WRF
    from .measurements import meteorological as meteo
    from .simulations import LSM
    from .simulations.LSM.DataLayer import SingleSimulation
    from .measurements import GIS
from .simulations import openfoam

"""
 0.3.0
 -----
    - Changed the datalayer.analysis to datalayer.cache. 
    - Adding more documentation. 
 
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
