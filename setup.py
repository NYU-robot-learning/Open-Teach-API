from setuptools import setup, find_packages

setup(
    name='openteach-api',
    version='1.0.0',
    packages=find_packages(),
    description='Deployment API for open-teach.',
    author='Aadhithya Iyer',
    install_requires = [
        'numpy',
        'blosc',
        'zmq'
    ]
)