from setuptools import setup

with open('README.md') as readme:
    long_desc = readme.read()


setup(
    name='NeoAlchemy',
    version='0.0.1',
    license='MIT',
    url='',

    description=("A toolkit for Neo4J inspired by SQLAlchemy's "
                 "Expression Language"),
    long_description=long_desc,
    keywords='Neo4J Graph Database',

    author='Two-Bit Alchemist',
    author_email='seregon@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
