import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iching_shifa",
    version="1.0",
    author="Ken Tang",
    author_email="kinyeah@gmail.com",
    description="A package of iching stalk divination (texts written in Traditional Chinese)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kentang2017/iching_shifa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)