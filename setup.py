from setuptools import setup, find_packages

setup(
    name='randrer',
    version='0.2.4',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'randrer = randrer.client.client:main'
        ]
    },
    url='',
    license='',
    author='Allie Fitter',
    author_email='afitter@cellcontrol.com',
    description='',
    install_requires=[
        'PyYAML',
        'xlib'
    ]
)
