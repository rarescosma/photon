from codecs import open
from os import path

from setuptools import setup, find_packages

dot = path.abspath(path.dirname(__file__))

# get the dependencies and installs
with open(path.join(dot, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if
                    x.startswith('git+')]

setup(
    name='photon',
    version='0.0.1',
    description='photo name matcher',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': ['photon=photon:cli'],
    },
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
)
