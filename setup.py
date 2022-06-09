

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="acss_core",
    version="0.0.1",
    author="Michael Boese",
    author_email="michael.boese@desy.de",
    description="Pipeline for accelerators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/desy-ml/acss-core",
    project_urls={
        "Bug Tracker": "https://github.com/desy-ml/acss-core/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=['confluent-kafka', 'requests', 'pyyaml', 'python-logstash', 'numpy', 'dacite', 'mysql-connector-python', 'accelerator-toolbox'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
