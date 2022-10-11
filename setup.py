from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='pyresparser',
    version='0.0.0',
    description='A simple resume parser used for extracting information from resumes',
    long_description=open('README.rst').read(),
    license='GPL-3.0',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    install_requires=[line.strip() for line in open("requirements.txt").readlines()],
    zip_safe=False,
    entry_points = {
        'console_scripts': ['pyresparser=pyresparser.command_line:main'],
    }
)
