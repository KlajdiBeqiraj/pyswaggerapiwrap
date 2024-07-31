from setuptools import setup, find_packages

setup(
    name='PySwaggerAPIWrap',
    version='0.1.2',
    description='A Python wrapper for API services that enables Swagger integration.',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='Klajdi Beqiraj',
    author_email='klajdibeqiraj96@gmail.com',
    url='https://github.com/KlajdiBeqiraj/PySwaggerAPIWrap.git',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Programming Language :: Python :: 3.9.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9'
)
