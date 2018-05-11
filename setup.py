import os
import re
from setuptools import setup

def get_version(*file_paths):
    """Retrieves the version from specific file"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

version = get_version("easy_backup", "__init__.py")
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(name='easy_backup',
      version=version,
      description='A script to create timestamped backups for local databases and data folders, and optionally rotate previous backups',
      long_description=readme + '\n\n' + history,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Database Engines/Servers',
      ],
      keywords='backup database',
      url='https://github.com/morlandi/easy_backup',
      author='Mario Orlandi',
      author_email='morlandi@brainstorm.it',
      license='MIT',
      scripts=['bin/easy_backup'],
      packages=['easy_backup'],
      # install_requires=[
      #     'markdown',
      # ],
      include_package_data=False,
      zip_safe=False)
