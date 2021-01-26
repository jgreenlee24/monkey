from setuptools import setup, find_packages


# with open('README.rst') as f:
#     readme = f.read()

# with open('LICENSE') as f:
#     license = f.read()

setup(
    name='sample',
    version='0.1.0',
    description='Scripts for the code monkey',
    # long_description=readme,
    author='Justin Greenlee',
    author_email='jgreenlee24@gmail.com',
    url='https://github.com/jgreenlee24/monkey',
    # license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)