__author__ = 'jomarko'

import os
from setuptools import setup, find_packages
from babel.messages import frontend as babel
from glob import *

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

data_files = [('/usr/lib/systemd/system', glob('systemd/*.service')),
              ('/usr/share/initial-setup/modules', glob('modules/*'))]

# add localization files
data_files += [('/usr/share/locale/%s/LC_MESSAGES' % dirname,
                ['locale/%s/LC_MESSAGES/initial-setup.mo' % dirname])
                for dirname in os.listdir("locale")
                if not dirname.endswith(".pot")]

setup(
    name = "initial-setup",
    version = "0.3.4",
    author = "Martin Sivak",
    author_email = "msivak@redhat.com",
    description='Post-installation configuration utility',
    url='http://fedoraproject.org/wiki/FirstBoot',
    license = "GPLv2+",
    keywords = "firstboot initial setup",
    packages = find_packages(),#####
    package_data = {
        "": ["*.glade"]
    },
    scripts = ["initial-setup", "firstboot-windowmanager"],######## !!!!! "&@" !!!!!
    data_files = data_files,
    setup_requires= ['nose>=1.0'],
    test_suite = "initial_setup",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ],
    cmdclass = {'compile_catalog': babel.compile_catalog,
                'extract_messages': babel.extract_messages,
                'init_catalog': babel.init_catalog,
                'update_catalog': babel.update_catalog}
)