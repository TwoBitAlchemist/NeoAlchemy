import os

import pytest

from neoalchemy import Graph


__TEST_LABEL__ = '__NEOALCHEMY_TEST__'


TEST_NEO_URL = os.environ.get('TEST_NEOALCHEMY_URL', None)
TEST_NEO_USER = os.environ.get('TEST_NEOALCHEMY_USER', None)
TEST_NEO_PASS = os.environ.get('TEST_NEOALCHEMY_PASS', None)
CAN_CLEAR_GRAPH = bool(os.environ.get('TEST_NEOALCHEMY_GRAPH_FULL_ACCESS', 0))
CAN_WRITE_GRAPH = (CAN_CLEAR_GRAPH or
                   bool(os.environ.get('TEST_NEOALCHEMY_GRAPH_ACCESS', 0)))


GRAPH_CLEARS_DISABLED_MSG = ("Graph clearing disabled. Enable with "
                             "`export TEST_NEOALCHEMY_GRAPH_FULL_ACCESS=1`\n"
                             "WARNING: THIS WILL DELETE YOUR ENTIRE GRAPH!!!")
GRAPH_WRITES_DISABLED_MSG = ("Graph writes disabled. Enable with "
                             "`export TEST_NEOALCHEMY_GRAPH_ACCESS=1`")

clears_graph = pytest.mark.skipif(not CAN_CLEAR_GRAPH,
                                  reason=GRAPH_CLEARS_DISABLED_MSG)
writes_required = pytest.mark.skipif(not CAN_WRITE_GRAPH,
                                     reason=GRAPH_WRITES_DISABLED_MSG)


test_graph = Graph(TEST_NEO_URL, user=TEST_NEO_USER, password=TEST_NEO_PASS)
