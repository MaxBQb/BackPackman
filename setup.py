from distutils.core import setup
from glob import glob

# noinspection PyUnresolvedReferences,PyPackageRequirements
import py2exe

setup(
    windows=['init.py'],
    name="BackPackman",
    version="0.0.1",
    author="MaxBQb",
    description="Brings Packman Back",
    data_files=[
        ('.', ["maze.txt"]),
        ('./images', glob('images/*')),
        ('./fonts', glob('fonts/*')),
    ],
    options={'py2exe': {'bundle_files': 2, 'compressed': True}},
    zipfile=None,
)
