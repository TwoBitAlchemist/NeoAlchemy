from setuptools import setup

with open('README.md') as readme:
    long_desc = readme.read()


setup(
    name='NeoAlchemy',
    version='0.8.0b',
    license='MIT',
    url='',

    description=('A microframework for Neo4J inspired by SQLAlchemy.'),
    long_description=long_desc,
    keywords='Neo4J Graph Database',

    author='Two-Bit Alchemist',
    author_email='seregon@gmail.com',

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
        'neo4j-driver',
        'six',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
