"""
Node superclass to define Instana endpoint nodes, GitHub file nodes and
method block nodes.
"""
from dataclasses import dataclass
import base64
from typing import Union
from pathlib import Path


class Node:
    """ Parent Node class. """

    @dataclass
    class EndpointNode:
        """
        Parse the responses from IBM Instana into an Endpoint node.
        """
        label: str
        technology: str
        latency: int

    class FileNode:
        """
        Node representing the GitHub file structure.
        """

        @dataclass
        class MethodNode:
            """
            Node holding the inner code blocks from the file structure.
            A file consists of method nodes.
            """
            parent: 'Node.FileNode'
            id: str
            params: str
            method: str
            decorator: Union[str, None] = None

            def __hash__(self):
                """
                Hash the node based on the method signature

                Returns:
                    The method's hash
                """
                return hash((self.id, self.params))

            def __eq__(self, comp):
                """
                Check the equality of a method, based on the method signature.

                Args:
                    comp: The method node to compare

                Returns:
                    True if equal, False otherwise
                """
                return (isinstance(comp, Node.FileNode.MethodNode) and
                        self.id == comp.id and
                        self.params == comp.params)

        def __init__(self, base_file):
            """
            Initialises the file structure based on the 
            GitHub file, the file's code and empty set of methods.

            Args:
                base_file: GitHub-fetched file, to extend.
            """
            self.base = base_file
            self.language = Path(base_file.path).suffix.replace(".", "")
            self.raw_code = base64.b64decode(self.base.content).decode()
            self.methods = {}


            """ Extends the methods of the current file.

                This is most often for the processing of import statements.

            Args:
                New methods to append to current structure
            """

        def extend(self, new_methods):
            """
            Extends the methods of the current file.
            When processing import statements, the file's method list
            is extended.

            Args:
                new_methods: The list of new methods to extend the file.
            """
            self.methods.update(new_methods)
