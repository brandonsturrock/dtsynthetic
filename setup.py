from distutils.core import setup

setup(
  name = 'dtsynthetic',         # How you named your package folder (MyLib)
  packages = ['dtsynthetic'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  description = 'Wrapper for the Dynatrace Synthetic API',   # Give a short description about your library
  author = 'Brandon Sturrock',                   # Type in your name
  author_email = 'brandon.sturrock@dynatrace.com',      # Type in your E-Mail
  url = 'https://github.com/brandonsturrock/dtsynthetic',   # Provide either the link to your github or to your website
  install_requires=[            # I get to this in a second
          'requests'
      ],
)