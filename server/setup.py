from setuptools import setup, find_packages

setup(
    name             = 'pi-mcqueen-server',
    version          = '0.1.0b1',
    description      = 'The Pi McQueen Server project', # Required
    long_description = open('README.rst').read(), # Optional
    url              = 'https://github.com/P403n1x87/pi-mcqueen', # Optional
    author           = 'Martina Pugliese, Gabriele N. Tornetta', # Optional
    author_email     = 'm.letitbe@gmail.com, phoenix1987@gmail.com', # Optional

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Topic :: Education',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='iot websockets',

    packages=find_packages(exclude=['test']),

    install_requires=[
        'RPi.GPIO',
        'websockets==4.0.1',
    ],

    entry_points={
        'console_scripts': [
            'pi-mcqueen-server=pi_mcqueen_server.__init__:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/P403n1x87/pi-mcqueen/issues',
        'Source': 'https://github.com/P403n1x87/pi-mcqueen/',
    },
)
