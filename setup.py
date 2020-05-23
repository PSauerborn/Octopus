from setuptools import setup
from setuptools import find_packages

setup(
  name='Octopus',
  version='0.0.5a',
  description='',
  author='Pascal Sauerborn',
  author_email='pascal.sauerborn@gmail.com',
  packages=find_packages(),
  install_requires=[
    'opentracing',
    'jaeger_client',
    'prometheus_client',
    'bottle',
    'requests'
  ]
)

