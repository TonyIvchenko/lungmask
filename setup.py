from pathlib import Path

import setuptools

README = Path(__file__).with_name("README.md")

setuptools.setup(
    name="lungmask",
    version="0.2.8",
    author="Johannes Hofmanninger",
    author_email="johannes.hofmanninger@meduniwien.ac.at",
    description="Package for automated lung segmentation in CT",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/TonyIvchenko/lungmask",
    project_urls={
        "Source": "https://github.com/TonyIvchenko/lungmask",
        "Upstream": "https://github.com/JoHof/lungmask",
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'lungmask = lungmask.__main__:main'
        ]
    },
    install_requires=[
        'pydicom',
        'numpy',
        'torch',
        'scipy',
        'SimpleITK',
        'tqdm',
        'scikit-image',
        'fill_voids'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)
