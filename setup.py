"""
PYSwaggerAPIWrap is a Python package designed to streamline interaction with online APIs that expose
Swagger documentation. With PYSwaggerAPIWrap, you can easily generate Python wrappers
for any API documented via Swagger, making it simpler to
integrate and utilize APIs in your code.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyswaggerapiwrap",
    version="0.1.8",
    description="A Python wrapper for API services that enables Swagger integration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Klajdi Beqiraj",
    author_email="klajdibeqiraj96@gmail.com",
    url="https://github.com/KlajdiBeqiraj/pyswaggerapiwrap.git",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.9.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
