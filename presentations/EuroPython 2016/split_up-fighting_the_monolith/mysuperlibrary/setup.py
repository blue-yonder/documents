from setuptools import setup, find_packages


setup(
    name='mypackage',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    include_package_data=True
)

