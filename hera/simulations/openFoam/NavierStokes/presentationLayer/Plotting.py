import pandas
import matplotlib.pyplot as plt
import math
from hera.simulations.openfoam.NavierStokes.preProcess import dataManipulations

class Plotting():

    _arrange = None

    def __init__(self):
        self._arrange=dataManipulations("")

    def variableAgainstDistance(self, data, variable, height, style="plot", colors=["red", "blue"], signedColors=["blue", "orange", "green", "red"],
                                signedDists=None, labels=None, topography=True, ax=None):
        """
        Plots the values of a variable and the terrain height in a slice along the distance downwind.
        Params:
            data: The data of the slice (pandas DataFrame)
            variable: The name of the column of the variable (string)
            colors: The colors of the plot, default red for the variable and blue for the terrain (list of two strings)
            signedDists: Default is None. Else, a list of distances that should be signed using a dashed line. (list of floats)
            signedColors: A list of colors to use for the signed distances (list of strings)
            labels: A list of labels for the two y axis and the x axis, default is ["Distance Downwind", variable, "Terrain"] (list of three strings)
            topography: If true, plots the terrain height.
            ax: ax in which to plot, default is None.
        Return: ax

        """
        if ax is None:
            fig, ax = plt.subplots()
        else:
            plt.sca(ax)

        # distances=[]
        # variables=[]
        # for dist in data.distance.drop_duplicates():
        #     if len(data.loc[data.distance == dist].loc[data.heightOverTerrain>height-10]) > 0 and len(data.loc[data.distance == dist].loc[data.heightOverTerrain<height+10]) > 0:
        #         d = data.loc[data.distance == dist]
        #         d2 = pandas.DataFrame([dict(distance=dist, heightOverTerrain=height)])
        #         value = d.append(d2).sort_values(by="heightOverTerrain").set_index("heightOverTerrain").interpolate(method='index').loc[height][variable]
        #         if math.isnan(value):
        #             pass
        #         else:
        #             variables.append(value)
        #             distances.append(dist)
        heightdata = self._arrange.makeSliceHeightData(data=data, height=height, variable=variable)

        data = data.sort_values(by="distance")
        labels = labels if labels is not None else ["Distance Downwind (m)", variable, "Terrain (m)"]

        getattr(ax, style)(heightdata.distance, heightdata[variable], color=colors[0])
        ax.tick_params(axis='y', labelcolor=colors[0])
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1], color=colors[0])
        if topography:
            ax2 = ax.twinx()
            ax2.plot(data.distance, data.terrain, color=colors[1])
            ax2.tick_params(axis='y', labelcolor=colors[1])
            ax2.set_ylabel(labels[2], color=colors[1])
        if signedDists is not None:
            for i in range(len(signedDists)):
                ax2.plot([signedDists[i],signedDists[i]], [data.z.min(), data.z.max()], color=signedColors[i], linestyle="--")
        return ax

    def UinLocations(self, data, points, style="plot", colors=["blue", "red"], labels=["Distance Downwind (m)", "Velocity (m/s)", "Height (m)"],ax=None):

        if ax is None:
            fig, ax = plt.subplots()
        else:
            plt.sca(ax)
        data = data.sort_values(by=["distance", "heightOverTerrain"])
        ax.plot(data.distance, data.terrain, zorder=10, color=colors[0])
        ax.set_ylim(data.z.min(), data.z.max())
        xticks = [i for i in range(int(data.Velocity.max()+2))]
        ax.set_ylabel(labels[2])
        ax.set_xlabel(labels[0])
        for point in points:
            axins = ax.inset_axes([point, data.loc[data.distance==point].terrain.mean(), data.distance.max()/10,
                                   data.z.max()-data.loc[data.distance==point].terrain.mean()], transform=ax.transData)
            getattr(axins, style)(data.loc[data.distance==point].sort_values(by=["distance", "heightOverTerrain"]).Velocity,
                    data.loc[data.distance==point].sort_values(by=["distance", "heightOverTerrain"]).z, color=colors[1], zorder=0)
            axins.set_ylim(data.loc[data.distance==point].terrain.mean(), data.loc[data.distance==point].z.max())
            axins.get_yaxis().set_visible(False)
            axins.xaxis.set_ticks_position("top")
            axins.xaxis.set_label_position("top")
            axins.set_xlim(0, data.Velocity.max()+0.5)
            axins.set_xticks(xticks)
            axins.set_xlabel(labels[1])
            ax.scatter(point, data.loc[data.distance==point].terrain.mean(), color=colors[1], zorder=15)

    def velocityInHeight(self, data, height):

        xs = []
        ys = []
        vels = []

        for x in data.query("heightOverTerrain>@height-2 and heightOverTerrain<@height+2").x.drop_duplicates():
            for y in data.query("heightOverTerrain>@height-2 and heightOverTerrain<@height+2").loc[data.x==x].y.drop_duplicates():
                if len(data.loc[data.x==x].loc[data.y==y].loc[data.heightOverTerrain > height - 2]) > 0 and len(
                       data.loc[data.x==x].loc[data.y==y].loc[data.heightOverTerrain < height + 2]) > 0:
                    d = data.loc[data.x==x].loc[data.y==y]
                    d2 = pandas.DataFrame([dict(x=x, y=y, heightOverTerrain=height)])
                    value = d.append(d2).sort_values(by="heightOverTerrain").set_index("heightOverTerrain").interpolate(
                        method='index').loc[height]["Velocity"]
                    if math.isnan(value):
                        pass
                    else:
                        vels.append(value)
                        xs.append(x)
                        ys.append(y)