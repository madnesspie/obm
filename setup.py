# Copyright 2020 Alexander Polishchuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import setuptools

import obm

EXTRAS_REQUIRE = {
    "tests": ["pytest", "python-dotenv", "pytest-xdist"],
    "lint": ["pylint", "mypy"],
    "docs": ["sphinx>=2.4,<3", "sphinx-rtd-theme"],
    "deploy": ["twine"],
    "dev": ["tox", "rope"],
}
EXTRAS_REQUIRE["dev"] += (
    EXTRAS_REQUIRE["tests"]
    + EXTRAS_REQUIRE["lint"]
    + EXTRAS_REQUIRE["docs"]
    + EXTRAS_REQUIRE["deploy"]
)


def read(file_name):
    with open(file_name) as f:
        content = f.read()
    return content


setuptools.setup(
    name="obm",
    version=obm.__version__,
    packages=setuptools.find_packages(exclude=["tests*"]),
    install_requires=["aiohttp>=3.6,<4", "web3>=5.7,<6", "marshmallow>=3.5,<4"],
    extras_require=EXTRAS_REQUIRE,
    license="Apache License 2.0",
    description="Async blockchain nodes interacting tool with ORM-like api.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/madnesspie/obm",
    author="Alexander Polishchuk",
    author_email="apolishchuk52@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
