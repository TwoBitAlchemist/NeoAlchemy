from setuptools import setup, find_packages


setup(
    name='neoalchemy',
    packages=find_packages(),
    version='0.8.0-beta.7',
    license='MIT',

    description=('A microframework for Neo4J inspired by SQLAlchemy.'),
    keywords=['neo4j', 'graph', 'database', 'cypher', 'ORM', 'OGM'],

    author='Two-Bit Alchemist',
    author_email='seregon@gmail.com',

    url='https://github.com/twobitalchemist/neoalchemy',
    download_url='https://github.com/twobitalchemist/neoalchemy/tarball/0.8.0b',

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
    ],

    install_requires=[
        'python-dateutil',
        'neo4j-driver',
        'six',
    ]
)
