from setuptools import setup

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

INSTALL_REQUIRES = ['setuptools']
with open('requirements.txt') as f:
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue
        INSTALL_REQUIRES.append(stripped)

PACKAGES = [
    'ab',
    'accounts',
    'admin_ext',
    'clutch',
    'clutchrpc',
    'clutchtunnel',
    'dashboard',
    'django_ext',
    'stats',
]

SCRIPTS = [
    'bin/clutch-web',
    'bin/clutch-tunnel',
    'bin/clutch-rpc',
    'bin/clutch-all',
    'bin/clutch-config',
    'bin/clutch-test',
]

setup(
    name='clutchserver',
    version='0.0.1',
    description='The server component for Clutch framework and Cluth A/B Testing.',
    long_description=LONG_DESCRIPTION,
    author='Eric Florenzano',
    author_email='eflorenzano@twitter.com',
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    setup_requires=['setuptools_git'],
    scripts=SCRIPTS,
)
