import paraview.simple as pvsimple
from ..postprocess.pvOpenFOAMBase import paraviewOpenFOAM
from ..postprocess.dataManipulations import dataManipulations
import numpy

class tests():

    _pvOFBase = None  # Holds the OF base.
    _casePath = None
    _manipulator = None

    @property
    def name(self):
        return self._name

    @property
    def pvOFBase(self):
        return self._pvOFBase

    def __init__(self, casePath, caseType='Decomposed Case', servername=None):
        """
        casePath: str
                A full path to the case directory.

        CaseType:  str
                Either 'Decomposed Case' for parallel cases or 'Reconstructed Case'
                for single processor cases.

        fieldnames: None or list of field names.  default: None.
                The list of fields to load.
                if None, read all fields

        servername: str
                if None, work locally.
                connection string to the paraview server.

                The connection string is printed when the server is initialized.

        """
        self._pvOFBase = paraviewOpenFOAM(casePath=casePath, caseType=caseType, servername=servername)
        self._casePath = casePath
        self._manipulator = dataManipulations()

    def getHeightSlice(self, percentage=90, fields="U", save=False, addToDB=False, key="Slice", path=None, projectName=None, hdfName="HeightSlice", **kwargs):
        """
        Returns a pandas dataframe of a z slice in height of desired percentage of the total height.
        """
        my_file = open('%s/system/blockMeshDict' % (self._casePath))
        string_list = my_file.readlines()
        my_file.close()
        for line in string_list:
            if "zMin" in line:
                line = line.replace(";","")
                zMin = int(line.split()[1])
                break
        for line in string_list:
            if "zMax" in line:
                line = line.replace(";","")
                zMax = int(line.split()[1])
                break
        height = (zMax-zMin)*percentage/100
        reader = pvsimple.FindSource("mainReader")
        filter = getattr(pvsimple, "Slice")(Input=reader, guiName="heightSlice")
        filter.SliceType.Normal = [0,0,1]
        filter.SliceType.Origin = [0,0,height]
        filter.UpdatePipeline()
        timelist = reader.TimestepValues

        data = self._pvOFBase._readTimeStep(filter, timelist[-1], fieldnames=fields, xarray=False)
        data["Velocity"] = numpy.sqrt(data["U_x"] * data["U_x"] + data["U_y"] * data["U_y"] + data["U_z"] * data["U_z"])

        self._manipulator.saveAndAddtoDB(save=save, addToDB=addToDB, data=data, path=path, key=key, projectName=projectName,
                                         filter=hdfName, height=height, **kwargs)

        return data

    def changeOfVelocityInHeight(self, save=False, addToDB=False, key="Slice", path=None, projectName=None, hdfName="VelocityDifference", **kwargs):
        """
        Returns a dataframe with the difference in velocity between adjacent points along z axis.
        """

        reader = pvsimple.FindSource("mainReader")
        timelist = reader.TimestepValues
        data = self._pvOFBase._readTimeStep(reader, timelist[-1], fieldnames="U", xarray=False)
        data["Velocity"] = numpy.sqrt(data["U_x"] * data["U_x"] + data["U_y"] * data["U_y"] + data["U_z"] * data["U_z"])
        data = data.sort_values(by=["x","y","z"])
        data = data.groupby(['x', "y"]).filter(lambda x: x.z.is_unique)
        data['diffs'] = data.groupby(['x', "y"])['Velocity'].transform(lambda x: x.diff()).fillna(0)

        self._manipulator.saveAndAddtoDB(save=save, addToDB=addToDB, data=data, path=path, key=key, projectName=projectName,
                                         filter=hdfName, **kwargs)

        return data

    def performAllTests(self, save=False, addToDB=False, path=None, projectName=None, **kwargs):
        """
        Performs all the tests on the data and returns a dictionary with the results.
        """
        height90data = self.getHeightSlice(save=save, addToDB=addToDB, path=path, projectName=projectName, **kwargs)
        changeOfVelocityData = self.changeOfVelocityInHeight(save=save, addToDB=addToDB, path=path, projectName=projectName, **kwargs)
        height90percentage = (height90data["Velocity"].max()-height90data["Velocity"].min())/height90data["Velocity"].min()*100
        ChangeWithHeight = False if len(changeOfVelocityData.loc[changeOfVelocityData.diffs<0])>0 else True
        results = dict(UalongXYdifference=height90percentage, UalongZconsistent=ChangeWithHeight)

        return results



