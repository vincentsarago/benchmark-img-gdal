from setuptools import setup, find_packages

with open("benchmark_img/__init__.py") as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

# Runtime requirements.
inst_reqs = ["click", "rasterio[s3]", "rio-tiler==1.0rc2"]

extra_reqs = {}


setup(
    name="benchmark_img",
    version=version,
    description=u"Benchmark for image creation using GDAL or PIL",
    long_description="",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="python gdal",
    author=u"",
    author_email="",
    url="",
    license="BSD",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
