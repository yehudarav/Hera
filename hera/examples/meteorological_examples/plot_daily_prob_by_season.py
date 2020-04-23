"""
=====================
plot contourf by seasons
=====================
"""
from hera import meteo
import seaborn
seaborn.set()

###############################################################################
# First, we read data from the data base:

projectName='IMS_Data'
stationName= 'AVNE ETAN'
station=meteo.IMS_getDocFromDB(projectName=projectName, StationName=stationName)
data=station[0].getData()
print(data)

###############################################################################
# Then, select a column from the data to plot:

print(data.columns)
print(station[0].desc['TD'])

plotfield='TD'

meteo.seasonplots.plotProbContourf_bySeason(data,plotfield)
