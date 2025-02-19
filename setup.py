# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tf2-hitsound-manager',
    version='1.2.0a1',
    description='A custom sound manager for Team Fortress 2',
    long_description=readme,
    author='gitchasing',
    url='https://github.com/gitchasing/tf2-hitsound-manager/',
    license=license,
    packages=find_packages(),
    install_requires=[
        'pydub~=0.25.1',
        'PyQt5~=5.15.11',
        'send2trash~=1.8.3'
    ],
    entry_points={
        "console_scripts":[
            "tf2-hitsound-manager=tf2_hitsound_manager:main",
        ],
    },
    package_data={
        "": ["assets/fonts/*.ttf", "assets/styles/*.qss", "data/*.txt", "data/*.csv"],
    },
    include_package_data=True,
)