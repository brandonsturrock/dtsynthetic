from distutils.core import setup

setup(
  name = 'dtsynthetic',
  packages = ['dtsynthetic'],
  version = '0.2.29',
  description = 'Wrapper for the Dynatrace Synthetic API',
  author = 'Brandon Sturrock',
  author_email = 'brandon.sturrock@dynatrace.com',
  url = 'https://github.com/brandonsturrock/dtsynthetic',
  install_requires=[
          'requests',
          'pandas'
      ],
)