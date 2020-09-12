from setuptools import find_packages, setup

setup(
    name='kdoorpi',
    version='0.0.0',
    author="Arti Zirk",
    author_email="arti@zirk.me",
    description="K-Space Door client that talks to the hardware",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[],
    extras_require={},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Networking',
        'Intended Audience :: System Administrators',
    ]

)
