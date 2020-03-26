import setuptools

import obm


def read(file_name):
    with open(file_name) as f:
        content = f.read()
    return content


setuptools.setup(
    name="obm",
    version=obm.__version__,
    packages=setuptools.find_packages(exclude=["tests*"]),
    install_requires=["aiohttp>=3.6,<4", "web3>=5.7,<6", "marshmallow>=3.5,<4"],
    extras_require={
        "dev": [
            "sphinx>=2.4,<3",
            "sphinx-rtd-theme",
            "python-dotenv",
            "pytest",
            "pylint",
            "mypy",
            "rope",
        ],
    },
    license="GNU Lesser General Public License v3 or later (LGPLv3+)",
    description="Async blockchain nodes interacting tool with ORM-like api.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    url="https://github.com/madnesspie/obm",
    author="Alexander Polishchuk",
    author_email="apolishchuk52@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
