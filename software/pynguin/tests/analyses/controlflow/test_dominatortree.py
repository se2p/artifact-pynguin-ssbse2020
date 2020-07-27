# This file is part of Pynguin.
#
# Pynguin is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pynguin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pynguin.  If not, see <https://www.gnu.org/licenses/>.
import sys

from bytecode import Bytecode

import pynguin.analyses.controlflow.cfg as cfg
import pynguin.analyses.controlflow.dominatortree as pdt
from tests.fixtures.programgraph.samples import for_loop


def test_integration_post_dominator_tree(conditional_jump_example_bytecode):
    control_flow_graph = cfg.CFG.from_bytecode(conditional_jump_example_bytecode)
    post_dominator_tree = pdt.DominatorTree.compute_post_dominator_tree(
        control_flow_graph
    )
    dot_representation = post_dominator_tree.to_dot()
    graph = """strict digraph  {
"ProgramGraphNode(9223372036854775807)";
"ProgramGraphNode(3)";
"ProgramGraphNode(2)";
"ProgramGraphNode(1)";
"ProgramGraphNode(0)";
"ProgramGraphNode(-1)";
"ProgramGraphNode(9223372036854775807)" -> "ProgramGraphNode(3)";
"ProgramGraphNode(3)" -> "ProgramGraphNode(2)";
"ProgramGraphNode(3)" -> "ProgramGraphNode(1)";
"ProgramGraphNode(3)" -> "ProgramGraphNode(0)";
"ProgramGraphNode(0)" -> "ProgramGraphNode(-1)";
}
"""
    assert dot_representation == graph
    assert post_dominator_tree.entry_node.index == sys.maxsize


def test_integration(small_control_flow_graph):
    post_dominator_tree = pdt.DominatorTree.compute_post_dominator_tree(
        small_control_flow_graph
    )
    dot_representation = post_dominator_tree.to_dot()
    graph = """strict digraph  {
"ProgramGraphNode(9223372036854775807)";
"ProgramGraphNode(2)";
"ProgramGraphNode(4)";
"ProgramGraphNode(3)";
"ProgramGraphNode(5)";
"ProgramGraphNode(6)";
"ProgramGraphNode(0)";
"ProgramGraphNode(9223372036854775807)" -> "ProgramGraphNode(2)";
"ProgramGraphNode(2)" -> "ProgramGraphNode(4)";
"ProgramGraphNode(2)" -> "ProgramGraphNode(3)";
"ProgramGraphNode(2)" -> "ProgramGraphNode(5)";
"ProgramGraphNode(5)" -> "ProgramGraphNode(6)";
"ProgramGraphNode(6)" -> "ProgramGraphNode(0)";
}
"""
    assert dot_representation == graph
    assert post_dominator_tree.entry_node.index == sys.maxsize


def test_integration_post_domination(larger_control_flow_graph):
    post_dominator_tree = pdt.DominatorTree.compute_post_dominator_tree(
        larger_control_flow_graph
    )
    node = [n for n in larger_control_flow_graph.nodes if n.index == 110][0]
    successors = post_dominator_tree.get_transitive_successors(node)
    successor_indices = {n.index for n in successors}
    expected_indices = {
        -sys.maxsize,
        1,
        2,
        3,
        5,
        100,
        120,
        130,
        140,
        150,
        160,
        170,
        180,
        190,
        200,
        210,
    }
    assert successor_indices == expected_indices


def test_integration_dominator_tree():
    for_loop_cfg = cfg.CFG.from_bytecode(Bytecode.from_code(for_loop.__code__))
    dom_tree = pdt.DominatorTree.compute(for_loop_cfg)
    # Every node of the cfg should be in the dominator tree
    assert for_loop_cfg.nodes == dom_tree.nodes
