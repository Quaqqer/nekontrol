from setuptools import setup

setup(
    name="nekontrol",
    version="0.1.1",
    package_dir={"nekontrol": "nekontrol"},
    install_requires=[
        "click==8.1.3",
        "termcolor==2.0.1",
        "requests==2.28.1",
        "appdirs==1.4.4",
        "natsort==8.2.0",
    ],
    entry_points={"console_scripts": ["nk = nekontrol.interactive.cli:cli"]},
)
