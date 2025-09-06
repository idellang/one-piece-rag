# build a basic setup.py file
from setuptools import setup, find_packages
setup(
    name='one_piece_rag',
    version='0.1.0',
    author='Led Castaneda',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'python-dateutil',
    ],
)
