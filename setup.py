from setuptools import setup

setup(
    name="kattest",
    version="0.1.0",
    package_dir={"kattest": "lib"},
    install_requires=[
        "click==8.1.3",
        "termcolor==2.0.1",
        "requests==2.28.1",
        "appdirs==1.4.4",
        "natsort==8.2.0",
    ],
    entry_points={"console_scripts": ["kattest = kattest.interactive.cli:cli"]},
)
