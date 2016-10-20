from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='yidashcam',
    version='0.7',
    description='An unofficial python library for interfacing with the Xiaomi YI Dash Cam.',
    long_description=long_description,
    url='https://github.com/kwirk/yidashcam',
    author='Steven Hiscocks',
    author_email='steven@hiscocks.me.uk',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='xiaomi yi dashcam',
    packages=['yidashcam'],
    install_requires=['requests'],
    extras_require={
        'webapp': ['Flask-Bootstrap'],
    },
    package_data={
        'yidashcam': ['templates/*.html'],
    },
    include_package_data=True,
    zip_safe=False,
)
