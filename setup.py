from setuptools import setup
import os, sys

def read(fname):
    # used to read the files like readme and requirements
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='Tasks',
      version='1.0',
      description='Tasks website and API to provide all kind of info about the tasks',
      long_description=read('README.rst'),
      author='Omar Aljazairy',
      url='git@git.cliqdigital.com:devops/nagios-keys.git',
      author_email='o.aljazairy@cliqdigital.com',
      packages=[
          'webtasks',
          'webtasks/webtasks',
          'webtasks/tasks',
          'webtasks/tests/tasks',
      ],
      keywords='tasks',
      install_requires=read('requirements.txt'),
      include_package_data=True,
      zip_safe=True)


# create the logs director if it doesn't exist
path = os.path.dirname(os.path.abspath(__file__))
directory = path + '/webtasks/logs'

if not os.path.exists(directory):
    os.makedirs(directory)
