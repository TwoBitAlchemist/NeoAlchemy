from setuptools import setup, find_packages


long_desc = """
NeoAlchemy is a SqlAlchemy-like tool for working with the Neo4J graph database
in Python. It is intended to be very easy to use, and intuitively familiar to
anyone who has used SqlAlchemy and/or the Cypher Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and only supports Neo4J
3.0+ connected over the Bolt protocol. It supports Python 2.7 and 3.3+.
"""


setup(
    name='neoalchemy',
    packages=find_packages(),
    version='0.9.0-beta.3',
    license='MIT',

    description=('A microframework for Neo4J inspired by SQLAlchemy.'),
    keywords=['neo4j', 'graph', 'database', 'cypher', 'ORM', 'OGM'],

    author='Two-Bit Alchemist',
    author_email='seregon@gmail.com',

    url='https://github.com/twobitalchemist/neoalchemy',
    download_url='https://github.com/twobitalchemist/neoalchemy/tarball/0.9.0b',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    install_requires=[
        'python-dateutil',
        'neo4j-driver',
        'six',
    ]
)
