import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PPPF',
    version='0.1.0',
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://linsalrob.github.io/PPPF/',
    license='MIT License',
    author='Rob Edwards',
    author_email='raedwards@gmail.com',
    description='Probabilistic Phage Protein Functions: Phage genomes and their annotations ',
    python_requires='>=3.6',
    install_requires=[
        'jsonpickle',
        'biopython',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    entry_points = {
        'console_scripts' : [
            'pppf_download_databases = pppf_databases:download_all_databases',
            'pppf_print_proteins = pppf_db:print_all_proteins',
            'pppf_list_genomes = pppf_db:list_all_genomes'
        ]
    }
)
