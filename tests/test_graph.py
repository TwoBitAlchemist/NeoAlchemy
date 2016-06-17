"""Graph (Connection Class) Tests"""
from neoalchemy import Graph


def test_default_connection():
    graph = Graph('bolt://localhost')
