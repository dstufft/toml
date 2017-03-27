#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name="toml",
    version="0.1.dev0",

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,

    install_requires=["anytree", "rply"],
)
