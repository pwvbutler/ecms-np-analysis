from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ecms_np_analysis', 
    version='0.1', 
    packages = find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements
)