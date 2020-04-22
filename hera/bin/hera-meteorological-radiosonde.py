import argparse
import pandas
from hera.measurements.meteorological.radiosonde import DataLayer

parser = argparse.ArgumentParser()
parser.add_argument('command', nargs=1, type=str)
parser.add_argument('args', nargs='*', type=str)
parser.add_argument('--coords', dest='coords', default=None, type=str)

args = parser.parse_args()


def load_handler(arguments):
    dl = DataLayer()

    loadDataInput = dict(projectName=arguments[0],
                         locationName=arguments[1],
                         date=arguments[2],
                         filePath=arguments[3]
                         )

    if args.coords is not None:
        coords = eval("%s" % args.coords)
        loadDataInput['latitude'] = coords[0]
        loadDataInput['longitude'] = coords[1]

    dl.loadData(**loadDataInput)


globals()['%s_handler' % args.command[0]](args.args)
