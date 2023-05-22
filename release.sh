#!/usr/bin/env bash

stubgen ./impick -o .
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
find impick -name "*.pyi" -type f -delete
rm -r dist build
