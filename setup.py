from setuptools import setup

setup(
    name="kattest",
    version="0.1.0",
    package_dir={"kattest": "lib"},
    install_requires=["click", "termcolor", "requests", "appdirs", "natsort"],
    entry_points={"console_scripts": ["kattest = kattest.interactive.cli:cli"]},
)
