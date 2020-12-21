import pandas
import dask
import os
from .... datalayer import project
from unum.units import *
from ...utils import toUnum, toNumber

class preProcess(project.ProjectMultiDBPublic):

    _publicProjectName = None
    _casePath = None
    _cloudName = None

    @property
    def casePath(self):
        return self._casePath

    @casePath.setter
    def casePath(self,newPath):
        self._casePath = newPath

    @property
    def cloudName(self):
        return self._cloudName

    @cloudName.setter
    def cloudName(self,newName):
        self._cloudName = newName

    def __init__(self, projectName, casePath, cloudName, databaseNameList=None, useAll=False,publicProjectName="OpenFOAMLSM"):
        """
        params:
        casePath = the path of the case
        cloudName = the name of the cloud, in which the particles' properties are saved.
        """
        self._publicProjectName = publicProjectName
        super().__init__(projectName=projectName,publicProjectName=publicProjectName,databaseNameList=databaseNameList,useAll=useAll)
        self._casePath = casePath
        self._cloudName = cloudName


    def extractFile(self,path,time,names,skiphead=20,skipend=4,vector=True):
        """
        Extracts data from a csv file.
        params:
        path: the path of the file
        time: the files' time step
        names: the names of the columns
        skiphead: number of lines to skip from the beginning of the file
        skipend: number of lines to skip from the ending of the file
        """
        newData = dask.dataframe.read_csv(path, skiprows=skiphead,
                                  skipfooter=skipend, engine='python', header=None, delim_whitespace=True, names=names)
        if vector:
            newData[names[0]] = newData[names[0]].str[1:]
            newData[names[2]] = newData[names[2]].str[:-1]
        newData["time"] = time
        return newData.astype(float)

    def extractRunResult(self, times = None, file=None, save=False, addToDB=True, withVelocity=False, withReleaseTimes=False,releaseTime=0, **kwargs):
        """
        Extracts results of an LSM run.
        parmas:
        times = a list of time steps to extract. If None, it extracts all time steps in the casePath.
        file = a name for a file, in which the data is saved. Default is "Positions.parquet", in the current working directory.
        save = a boolian parameter, to choose whether to save the data. default is False.
        addToDB = a boolian parameter, to choose whether to save the data. default is True. It is used only if save is True.
        withVelocity = set to True in order to extract the particles' velocities in addition to their positions. Default is False.
        **kwargs = any additional parameters to add to the description in the DB.
        """
        data = dask.dataframe.from_pandas(pandas.DataFrame(),npartitions=2)

        times = os.listdir(self.casePath) if times is None else times
        for filename in times:
            try:
                newData = self.extractFile(f"{self.casePath}/{filename}/lagrangian/{self.cloudName}/globalPositions",filename,['x', 'y', 'z'])
                if withVelocity:
                    dataU = self.extractFile(f"{self.casePath}/{filename}/lagrangian/{self.cloudName}/U",filename,['U_x', 'U_y', 'U_z'])
                    for col in ['U_x', 'U_y', 'U_z']:
                        newData[col] = dataU[col]
                if withReleaseTimes:
                    dataM = self.extractFile(f"{self.casePath}/{filename}/lagrangian/{self.cloudName}/age",filename,['age'],vector=False)
                    newData["releaseTime"] = dataM["time"]-dataM["age"]+releaseTime
                data=data.append(newData)
            except:
                pass
        if save:
            cur = os.getcwd()
            file = os.path.join(cur,f"{self.cloudName}Positions.parquet") if file is None else file
            data.to_parquet(file, compression="GZIP")
            if addToDB:
                self.addSimulationsDocument(resource=file,dataFormat="parquet",type="LSMPositions",
                                            desc=dict(casePath=self.casePath,cloudName=self.cloudName,**kwargs))
        return data

    def getConcentration(self, nParticles, endTime, startTime=1, Q=1*kg, dx=10 * m, dy=10 * m, dz =10 * m, dt =10 * s,
                         Qunits=mg, lengthUnits=m, timeUnits=s, save=False, addToDB=True, file=None,releaseTime=0, **kwargs):
        """
        Calculates the concentration of dispersed particles.
        parmas:
        nParticles = The total number of particles induced to the system at all times.
        endTime = The final time step to read.
        startTime = The first time step to read. The default is 1.
        Q = The total mass of particles induced to the system. The default is 1 kg.
        dx = The distance between grid points of the concentration field in the x direction. The default is 10 meters.
        dy = The distance between grid points of the concentration field in the y direction. The default is 10 meters.
        dz = The distance between grid points of the concentration field in the z direction. The default is 10 meters.
        dt = The time measure between grid points of the concentration field. The default is 10 seconds.
        Qunits = The mass units of the concentration in the final dataframe. The default is mg.
        lengthUnits = The length units of the concentration in the final dataframe. The default is meter.
        timeUnits = The time units of the time steps in the final dataframe. The default is second.
        file = a name for a file, in which the data is saved. Default is "Concentration.parquet", in the current working directory.
        save = a boolian parameter, to choose whether to save the data. default is False.
        addToDB = a boolian parameter, to choose whether to save the data. default is True. It is used only if save is True.
        **kwargs = any additional parameters to add to the description in the DB.
        """
        dx = toNumber(toUnum(dx, lengthUnits), lengthUnits)
        dy = toNumber(toUnum(dy, lengthUnits), lengthUnits)
        dz = toNumber(toUnum(dz, lengthUnits), lengthUnits)
        dt = int(toNumber(toUnum(dt, timeUnits), timeUnits))
        withReleaseTimes=False
        if type(Q)==list:
            if len(Q) != endTime-startTime+1:
                raise KeyError("Number of values in Q must be equal to the number of time steps!")
            Q = [toNumber(toUnum(q, Qunits),Qunits) for q in Q]
            releaseTimes = [releaseTime+ i for i in range(int(endTime-startTime+1))]
            dataQ = pandas.DataFrame({"releaseTime":releaseTimes,"Q":Q})
            withReleaseTimes = True
        else:
            Q = toNumber(toUnum(Q, Qunits),Qunits)
        datalist = []
        for time in [startTime + dt * i for i in range(int((endTime-startTime) / dt))]:
            data = self.extractRunResult(times=[t for t in range(time, time + dt)], withReleaseTimes=withReleaseTimes,releaseTime=releaseTime)
            data["x"] = (data["x"] / dx).astype(int) * dx + dx / 2
            data["y"] = (data["y"] / dy).astype(int) * dy + dy / 2
            data["z"] = (data["z"] / dz).astype(int) * dz + dz / 2
            data["time"] = ((data["time"]-1) / dt).astype(int) * dt + dt
            if type(Q)==list:
                data = data.set_index("releaseTime").join(dataQ.set_index("releaseTime")).reset_index()
            else:
                data["Q"] = Q
            data["Dosage"] = data["Q"] / (nParticles * dx * dy * dz)
            data = data.drop(columns="Q")
            data = data.groupby(["x","y","z","time"]).sum()
            data["Concentration"] = data["Dosage"] / dt
            datalist.append(data.compute())
            print(f"Finished times {time} to {time+dt}")
        data = pandas.concat(datalist).reset_index()

        if save:
            cur = os.getcwd()
            file = os.path.join(cur,f"{self.cloudName}Concentration.parquet") if file is None else file
            data.to_parquet(file, compression="GZIP")
            if addToDB:
                self.addSimulationsDocument(resource=file, dataFormat="parquet", type="openFoamLSMrun",
                                            desc=dict(casePath=self.casePath, cloudName=self.cloudName,
                                                      startTime=startTime, endTime=endTime, Q=Q, dx=dx,
                                                      dy=dy, dz=dz, dt=dt,nParticles=nParticles, **kwargs))

        return data

    def makePointSource(self, x, y, z, nParticles):
        """
        Writes an instantaneous point source for the run.
        params:
        x = The x coordinate of the source.
        y = The y coordinate of the source.
        z = The z coordinate of the source.
        nParticles = The number of particles.
        """
        string = "/*--------------------------------*- C++ -*----------------------------------*\n " \
                 "| =========                 |                                                 |\n" \
                 "| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n" \
                 "|  \    /   O peration     | Version:  dev                                   |\n" \
                 "|   \  /    A nd           | Web:      www.OpenFOAM.org                      |\n" \
                 "|    \/     M anipulation  |                                                 |\n" \
                 "\*---------------------------------------------------------------------------*/\n" \
                 "FoamFile\n{    version     2.0;\n    format      ascii;\n    class       vectorField;\n" \
                 "    object      kinematicCloudPositions;\n}\n" \
                 "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n" \
                 f"{nParticles}\n(\n"
        for i in range(nParticles):
            string += f"({x} {y} {z})\n"
        string += ")\n"
        with open(os.path.join(self.casePath,"constant","kinematicCloudPositions"),"w") as writeFile:
            writeFile.write(string)