from setuptools import setup, find_packages

setup(
    name="testcrafter",
    version="0.1.0",
    author="Your Name",
    description="The Ultimate ADO Test & Page Artifact Generator",
    packages=find_packages(),
    py_modules=["testcrafter"],
    install_requires=[
        "requests>=2.28.0",
        "PyYAML>=6.0"
    ],
    entry_points={
        "console_scripts": [
            "testcrafter=testcrafter:main"
        ]
    },
)
