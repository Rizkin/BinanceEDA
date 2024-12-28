from setuptools import setup, find_packages

setup(
    name="binance_eda",  # Name of your package
    version="0.1",            # Initial version
    packages=find_packages(), # Automatically find all sub-packages
    install_requires=[
        "python-binance"      # Add any dependencies (e.g., python-binance)
    ],
    description="Experiments in Python algo trading",
    author="Rizwan Moidunni",
    author_email="riz1000@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
