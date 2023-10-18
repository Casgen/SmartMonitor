from setuptools import setup

setup(
    name="SmartMonitor",
    version="0.0.1",
    package=["smartmonitor"],
    entry_points={
            "console_scripts": [
                "smartmonitor = smartmonitor.if __main__:main"

            ]
    },
)
