from graphviz import Digraph
import tempfile
import uuid
from pm4py.objects.process_tree import process_tree, tree_constants

DEFAULT_CIRCLE_WIDTH = 0.6
DEFAULT_CIRCLE_FONT_SIZE = 14
DEFAULT_BOX_WIDTH = 2.5
DEFAULT_BOX_FONT_SIZE = 8

def repr_tree(tree, viz, current_node, rec_depth, parameters):
    """
    Represent a subtree on the GraphViz object

    Parameters
    -----------
    tree
        Current subtree
    viz
        GraphViz object
    current_node
        Father node of the current subtree
    rec_depth
        Reached recursion depth
    parameters
        Possible parameters of the algorithm:
            circle_width -> Width of the circles containing the operators
            circle_font_size -> Font size associated to the operators
            box_width -> Width of the box associated to the transitions
            box_font_size -> Font size associated to the transitions boxes

    Returns
    -----------
    gviz
        (partial) GraphViz object
    """
    for child in tree.children:
        if type(child) is process_tree.PT_Transition:
            viz.attr('node', shape='box', fixedsize='true', width=parameters["box_width"], fontsize=parameters["box_font_size"])
            this_trans_id = str(uuid.uuid4())
            if child.label is None:
                viz.node(this_trans_id, repr(child), style='filled', fillcolor='black')
            else:
                viz.node(this_trans_id, repr(child))
            viz.edge(current_node, this_trans_id)
        elif type(child) is process_tree.ProcessTree:
            condition_wo_operator = child.operator == tree_constants.EXCLUSIVE_OPERATOR and len(
                child.children) == 1 and type(
                child.children[0]) is process_tree.PT_Transition
            if condition_wo_operator:
                childchild = child.children[0]
                viz.attr('node', shape='box', fixedsize='true', width=parameters["box_width"], fontsize=parameters["box_font_size"])
                this_trans_id = str(uuid.uuid4())
                if childchild.label is None:
                    viz.node(this_trans_id, repr(childchild), style='filled', fillcolor='black')
                else:
                    viz.node(this_trans_id, repr(childchild))
                viz.edge(current_node, this_trans_id)
            else:
                viz.attr('node', shape='circle', fixedsize='true', width=parameters["circle_width"], fontsize=parameters["circle_font_size"])
                op_node_identifier = str(uuid.uuid4())
                viz.node(op_node_identifier, child.operator)
                viz.edge(current_node, op_node_identifier)
                viz = repr_tree(child, viz, op_node_identifier, rec_depth+1, parameters)
    return viz

def apply(tree, parameters=None):
    """
    Obtain a Process Tree representation through GraphViz

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm:
            circle_width -> Width of the circles containing the operators
            circle_font_size -> Font size associated to the operators
            box_width -> Width of the box associated to the transitions
            box_font_size -> Font size associated to the transitions boxes
    variant
        Variant of the algorithm to use

    Returns
    -----------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    if not "circle_width" in parameters:
        parameters["circle_width"] = str(DEFAULT_CIRCLE_WIDTH)
    if not "circle_font_size" in parameters:
        parameters["circle_font_size"] = str(DEFAULT_CIRCLE_FONT_SIZE)
    if not "box_width" in parameters:
        parameters["box_width"] = str(DEFAULT_BOX_WIDTH)
    if not "box_font_size" in parameters:
        parameters["box_font_size"] = str(DEFAULT_BOX_FONT_SIZE)

    parameters["circle_width"] = str(parameters["circle_width"])
    parameters["circle_font_size"] = str(parameters["circle_font_size"])
    parameters["box_width"] = str(parameters["box_width"])
    parameters["box_font_size"] = str(parameters["box_font_size"])

    format = parameters["format"] if "format" in parameters else "png"

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("pt", filename=filename.name, engine='dot')

    # add first operator
    if tree.operator:
        viz.attr('node', shape='circle', fixedsize='true', width=parameters["circle_width"], fontsize=parameters["circle_font_size"])
        op_node_identifier = str(uuid.uuid4())
        viz.node(op_node_identifier, tree.operator)

        viz = repr_tree(tree, viz, op_node_identifier, 0, parameters)

    viz.attr(overlap='false')
    viz.attr(fontsize='11')
    viz.format = format

    return viz