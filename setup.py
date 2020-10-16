from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fordpass',
    version='0.0.2',
    author="Dave Clarke",
    author_email="info@daveclarke.me",
    description="Python wrapper for the FordPass API for Ford vehicle information and control: start, stop, lock, unlock.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clarkd/fordpass-python",
    license="MIT",
    packages=['fordpass'],
    scripts=['fordpass/bin/demo.py'],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests']
)