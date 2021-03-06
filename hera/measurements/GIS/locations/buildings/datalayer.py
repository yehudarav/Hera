import os
import logging
import pandas
import geopandas
from .. import abstractLocation
from .analysis import analysis
from .....toolkit import TOOLKIT_SAVEMODE_NOSAVE,TOOLKIT_SAVEMODE_ONLYFILE,TOOLKIT_SAVEMODE_ONLYFILE_REPLACE,TOOLKIT_SAVEMODE_FILEANDDB,TOOLKIT_SAVEMODE_FILEANDDB_REPLACE


from .....datalayer import datatypes,nonDBMetadataFrame

try:
    from freecad import app as FreeCAD
    import Part
    import Mesh
except ImportError as e:
    logging.warning("Loading the Building Toolkit. FreeCAD not Found, cannot convert to STL")


class BuildingsToolkit(abstractLocation.AbstractLocationToolkit):
    """
        Toolkit to manage the buildings.

        Reading the shapefile with geoDataFrame will result in dataframe
        with the following columns:

        - geometry: the polygon of the building
        - Building height column : the column name is in BuildingHeightColumn
                                    default value: BLDG_HT
        - Land height  : the columns name is in LandHeightColumn
                                default value: HT_LAND
    """

    _BuildingHeightColumn = None

    @property
    def BuildingHeightColumn(self):
        return self._BuildingHeightColumn

    @BuildingHeightColumn.setter
    def BuildingHeightColumn(self, value):
        self._BuildingHeightColumn = value

    @property
    def LandHeightColumn(self):
        return self._LandHeightColumns

    @LandHeightColumn.setter
    def LandHeightColumn(self, value):
        self._LandHeightColumns = value


    def __init__(self, projectName, FilesDirectory=None):

        super().__init__(projectName=projectName,toolkitName="Buildings",FilesDirectory=FilesDirectory)
        self._analysis = analysis(dataLayer=self)

        self._BuildingHeightColumn = "BLDG_HT"
        self._LandHeightColumns   = 'HT_LAND'

    @property
    def doctype(self):
        return f"{self.name}_STL"

    def toSTL(self, regionNameOrData, outputFileName,flat=None,saveMode=TOOLKIT_SAVEMODE_FILEANDDB_REPLACE):
        """
            Converts the document to the stl and saves it to the disk.
            Adds the stl file to the DB.


            Parameters
            ----------

            regionNameOrData: str or geopandas .
                The name of the datasource or the geopandas file to convert.

                If geopandas has the following columns:

            flat: None or float.
                The base of the building.
                If None, use the buildings height.

            outputfile: str
                a path to the output file.

            saveMode: str
                - None, does not add to the DB.
                - toolkit.TOOLKIT_SAVEMODE_FILEANDDB_REPLACE replace the document if exists
                - toolkit.TOOLKIT_SAVEMODE_FILEANDDB         throws exception.

            Returns
            -------
                The maximal height

        """

        maxheight = -500

        FreeCADDOC = FreeCAD.newDocument("Unnamed")

        if isinstance(regionNameOrData,str):
            shp = self.getLocationByRegion(regionNameOrData).getData()
        else:
            shp = regionNameOrData

        k = -1
        for j in range(len(shp)):  # converting al the buildings
            try:
                walls = shp['geometry'][j].exterior.xy
            except:
                continue

            if j % 100 == 0:
                self.logger.execution(f"{j} shape file is executed. Length Shape: {len(shp)}")

            k = k + 1
            wallsheight = shp[self.BuildingHeightColumn][j]
            if flat is None:
                altitude = shp[self.LandHeightColumn][j]
            else:
                altitude = flat

            FreeCADDOC.addObject('Sketcher::SketchObject', 'Sketch' + str(j))
            FreeCADDOC.Objects[2 * k].Placement = FreeCAD.Placement(FreeCAD.Vector(0.000000, 0.000000, 0.000000),  # 2*k-1
                                                             FreeCAD.Rotation(0.000000, 0.000000, 0.000000, 1.000000))

            for i in range(len(walls[0]) - 1):
                FreeCADDOC.Objects[2 * k].addGeometry(Part.Line(FreeCAD.Vector(walls[0][i], walls[1][i], altitude),
                                                         FreeCAD.Vector(walls[0][i + 1], walls[1][i + 1], altitude)))

            FreeCADDOC.addObject("PartDesign::Pad", "Pad" + str(j))
            FreeCADDOC.Objects[2 * k + 1].Sketch = FreeCADDOC.Objects[2 * k]
            buildingTopAltitude = wallsheight + altitude  # wallsheight + altitude
            maxheight = max(maxheight, buildingTopAltitude)
            FreeCADDOC.Objects[2 * k + 1].Length = buildingTopAltitude  # 35.000000
            FreeCADDOC.Objects[2 * k + 1].Reversed = 0
            FreeCADDOC.Objects[2 * k + 1].Midplane = 0
            FreeCADDOC.Objects[2 * k + 1].Length2 = wallsheight  # 100.000000
            FreeCADDOC.Objects[2 * k + 1].Type = 0
            FreeCADDOC.Objects[2 * k + 1].UpToFace = None


        FreeCADDOC.recompute() # maybe it should be in the loop.


        outputfileFull = os.path.abspath(os.path.join(self.FilesDirectory,outputFileName))
        Mesh.export(FreeCADDOC.Objects, outputfileFull)

        if saveMode in [TOOLKIT_SAVEMODE_FILEANDDB_REPLACE,
                        TOOLKIT_SAVEMODE_FILEANDDB]:

            regionNameSTL = outputFileName.split(".")[0] if "." in outputFileName else outputFileName

            doc = self.getSTL(regionNameSTL)

            if doc is not None and saveMode == TOOLKIT_SAVEMODE_FILEANDDB:
                raise ValueError(f"STL {regionNameSTL} exists in project {self.projectName}")

            desc = {
                    abstractLocation.TOOLKIT_LOCATION_REGIONNAME: regionNameSTL,
                    abstractLocation.toolkit.TOOLKIT_TOOLKITNAME_FIELD : self.toolkitName
                   }

            if doc is None:
                self.addCacheDocument(type=self.doctype,
                                      resource=outputfileFull,
                                      dataFormat=datatypes.STRING,
                                      desc=desc)
            else:
                doc.resource = outputfileFull
                doc.desc = desc
                doc.save()



        self.logger.info(f"toSTL: end. Maxheight {maxheight}")
        return maxheight

    def getSTL(self,regionNameSTL):
        """
            Retrive the STL from the DB

        Parameters
        ----------
        regionNameSTL: str
            The name of the regiona name STL.

        Returns
        -------
            The document of the STL.
        """
        desc = {
                abstractLocation.TOOLKIT_LOCATION_REGIONNAME: regionNameSTL,
                "type" : self.doctype
                }
        docList = self.getCacheDocuments(**desc)
        return None if len(docList)==0 else docList[0]


    def loadData(self, fileNameOrData, saveMode=TOOLKIT_SAVEMODE_NOSAVE, regionName=None, additionalData=dict()):
        """
            Loading a data from file and possibly saves to the DB.
            Manages the parsing of the datafile.

        Parameters
        ----------
        fileNameOrData: str
                If str , the datafile to load
                If other objects - convert the

        saveMode: str
                Can be either:

                    - TOOLKIT_SAVEMODE_NOSAVE   : Just load the data from file and return the datafile

                    - TOOLKIT_SAVEMODE_ONLYFILE : Loads the data from file and save to a file.
                                                  raise exception if file exists.

                    - TOOLKIT_SAVEMODE_ONLYFILE_REPLACE: Loads the data from file and save to a file.
                                                  Replace the file if it exists.

                    - TOOLKIT_SAVEMODE_FILEANDDB : Loads the data from file and save to a file and store to the DB as a source.
                                                    Raise exception if the entry exists.

                    - TOOLKIT_SAVEMODE_FILEANDDB_REPLACE: Loads the data from file and save to a file and store to the DB as a source.
                                                    Replace the entry in the DB if it exists.



        regionName: str
            optional name for the datasource.

        additionalData: dict
             additional metadata if adding to the DB


        Returns
        -------
            Document with the data

        """

        if isinstance(fileNameOrData,str):
            if os.path.exists(os.path.abspath(fileNameOrData)):
                regionName = os.path.basename(fileNameOrData).split(".")[0] if regionName is None else regionName
                data = geopandas.read_file(fileNameOrData)
            else:
                raise FileNotFoundError(f"The {fileNameOrData} does not exist.")

        else:
            data = fileNameOrData

        doc = None

        if saveMode in [TOOLKIT_SAVEMODE_ONLYFILE,
                        TOOLKIT_SAVEMODE_ONLYFILE_REPLACE,
                        TOOLKIT_SAVEMODE_FILEANDDB,
                        TOOLKIT_SAVEMODE_FILEANDDB_REPLACE]:

            outputFileName = os.path.join(self.FilesDirectory, f"{regionName}.shp")

            if saveMode in [TOOLKIT_SAVEMODE_FILEANDDB,TOOLKIT_SAVEMODE_ONLYFILE]:
                if os.path.exists(outputFileName):
                    raise FileExistsError(f"{outputFileName} exists in project {self.projectName}")

            data.to_file(outputFileName)

            if saveMode in [TOOLKIT_SAVEMODE_FILEANDDB,TOOLKIT_SAVEMODE_FILEANDDB_REPLACE]:

                doc = self.getDatasourceData(regionName)
                if doc is not None and saveMode==TOOLKIT_SAVEMODE_FILEANDDB:
                    raise ValueError(f"{regionName} exists in DB for project {self.projectName}")

                additionalData[abstractLocation.TOOLKIT_LOCATION_REGIONNAME] =  regionName

                if doc is None:
                    doc = self.addDataSource(dataSourceName=regionName,
                                               resource=outputFileName,
                                               dataFormat=datatypes.GEOPANDAS,
                                               **additionalData)

                else:
                    doc['resource'] = outputFileName
                    doc.desc = additionalData
                    doc.save()

        return nonDBMetadataFrame(data) if doc is None else doc