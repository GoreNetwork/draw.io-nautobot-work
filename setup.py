from setuptools import setup
from setuptools import find_packages

with open('README.md', mode='r') as readme:
    long_description = readme.read()

setup(
    name='nautobot_plugin_builder',
    version = '1.0.0',
    author = "Daniel Himes",
    author_email = 'dhimes@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description = 'Builds out the base of a Nautobot plugin from a draw.io database drawing',
    install_requires = [
        'PyYAML==6.0',
        'xmltodict==0.13.0',
        ],
    url = 'https://github.com/GoreNetwork/draw.io-nautobot-work',
    packages=find_packages( where="./src"),
    package_dir={"":'src'},
    python_requires = ">=3.7",
    )