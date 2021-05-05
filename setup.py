import setuptools
import re
import os

# Load description from the README
with open('README.md', "r") as fh:
    long_description = fh.read()

# Load version from the module init
with open(os.path.join('brunhilda', '__init__.py'), 'r', encoding='utf-8') as fh:
    content = fh.read()
    reg = re.compile(r"__version__\s*=\s*['\"]([\w\d\.\+\-]+)['\"]")
    version = reg.search(content).group(1)

setuptools.setup(
    name="brunhilda",
    version=version,
    author="Bender Robotics",
    author_email="kumpan@benderrobotics.com",
    description="Bender Robotics System Test Runner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.benderrobotics.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'Jinja2>=2.10.3',
        'numpy>=1.17.3',
        'ddt>=1.2.2',
        'colorama>=0.4.1',
        'docutils>=0.15.2',
        'Pillow>=7.2.0',
    ]
)
