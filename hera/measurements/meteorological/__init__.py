#<<<<<<< HEAD
#from hera.measurements.meteorological.highfreqdata.datalayer import getTurbulenceCalculator
#
# from .datalayer import DataLayer_IMS
# IMS_datalayer = DataLayer_IMS()
#
# from .datalayer import DataLayer_CampbellBinary
# CampbellBinary_datalayer = DataLayer_CampbellBinary()
#
# # from .imsdata import getDocFromFile as IMS_getDocFromFile
# # from .imsdata import getDocFromDB   as IMS_getDocFromDB
#
# from hera.measurements.meteorological.IMS.dailyClimatology import calcHourlyDist
#
from hera.measurements.meteorological.IMS.presentationLayer import DailyPlots
# IMS_dailyplots = DailyPlots()
#
# from hera.measurements.meteorological.IMS.presentationLayer import SeasonalPlots
# IMS_seasonplots=SeasonalPlots()
#
# from hera.measurements.meteorological.IMS.dateManipulation import *

#from .datalayer import getTurbulenceCalculator

from .datalayer import DataLayer_IMS
IMS_datalayer = DataLayer_IMS()

from .datalayer import DataLayer_CampbellBinary
CampbellBinary_datalayer = DataLayer_CampbellBinary()

from .parserClasses import CampbellBinaryInterface

# from .imsdata import getDocFromFile as IMS_getDocFromFile
# from .imsdata import getDocFromDB   as IMS_getDocFromDB

#from .analytics.dailyClimatology import calcHourlyDist

#from .presentationlayer.dailyClimatology import DailyPlots
#IMS_dailyplots = DailyPlots()

#from .presentationlayer.dailyClimatology import SeasonalPlots
#IMS_seasonplots=SeasonalPlots()

#from .analytics.dateManipulation import *
#>>>>>>> remotes/origin/davidg



