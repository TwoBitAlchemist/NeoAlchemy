##########
NeoAlchemy
##########

NeoAlchemy is a microframework for working with the Neo4J graph database
inspired by SqlAlchemy. It is intended to be very easy to use, and intuitively
familiar to anyone who has used SqlAlchemy and/or the Cypher Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and only supports Neo4J
3.0+ connected over the Bolt protocol. It supports Python 2.7 and 3.3+.

If you don't have Neo4J installed, `do that first`_. Make sure to install
version 3.0 or higher! If you don't have an environment set up, consider
`setting up a virtual environment`_.


.. _do that first: https://neo4j.com/download/
.. _setting up a virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/

------------------------------------------------------------------------------

.. toctree::
   :maxdepth: 3

   intro
   apis
   query-builder
   schema-OGM
   schema-classes
   querybuilder-classes
   OGM-classes
   roadmap
