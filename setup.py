from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='cyberpandas',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='IP Address type for pandas',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ContinuumIO/cyberpandas',
    author='Tom Augspurger',
    author_email='tom.w.augspurger@gmail.com',
    license="BSD",
    classifiers=[  # Optional
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=[
        'pandas>=0.23.0',
    ]
)
