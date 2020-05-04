import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PPPF-linsalrob',
    version='0.0.1',
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://linsalrob.github.io/PPPF/',
    license='MIT License',
    author='Rob Edwards',
    author_email='raedwards@gmail.com',
    description='Phage genomes and their annotations ',
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
)
