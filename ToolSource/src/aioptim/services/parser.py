"""
Component to parse methods from the Java, Python files.
Methods involved in processing a request are sequenced into a list.
"""
from aioptim.utils.node import Node
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_python as tspython
from rapidfuzz import fuzz
from collections import deque
from abc import abstractmethod, ABC


class BaseParser(ABC):
    """ Base parser class providing the shared functionality """

    def parse_file_methods(self, file):
        """
        Retrives all the methods in a given file.
        This updates the file's internal dictionary

        Args:
            file: The file to operate on
        """
        def process_match(matches):
            for match in matches:
                matched_items = match[1]
                method_signature = matched_items['identifier'][0].text.decode()
                parameters = matched_items['parameters'][0].text.decode()
                decorator = matched_items.get('decorator', None)
                if decorator:
                    decorator = decorator[0].text.decode()
                method = matched_items['method'][0].text.decode()
                file.methods[
                    method_signature
                ] = Node.FileNode.MethodNode(
                    parent=file,
                    id=matched_items['identifier'][0].text.decode(),
                    params=parameters,
                    method=method,
                    decorator=decorator
                )

        tree = self.parser.parse(file.raw_code.encode())
        process_match(self.queries['method_query'].matches(tree.root_node))
        process_match(self.queries['decorator_query'].matches(tree.root_node))

    def parse_method_calls(self, method_node):
        """
        Creates a method trace beginning at the given method.

        This utilises the created call graph and simply traverses it
        through the use of a BFS algorithm.

        Args:
            method_node: The method node from where to begin the trace
        """
        def method_call(call):
            return call.split("(")[0].split(".")[-1]
        if not method_node:
            return
        fault_line = set()
        queue = deque([method_node])
        while queue:
            node = queue.popleft()
            fault_line.add(node)
            tree = self.parser.parse(node.method.encode())
            matches = self.queries['call'].matches(tree.root_node)
            for match in matches:
                call = method_call(match[1]['call'][0].text.decode())
                if (call in node.parent.methods and
                        node.parent.methods[call] not in fault_line):
                    queue.append(node.parent.methods[call])
        return fault_line

    def endpoint(self, files, endpoint_ref):
        """
        Given a label to the endpoint, this method seeks
        to match on this endpoint through the use of fuzzy matching.

        Args:
            files: The list of files to search from
            endpoint_ref: A label for the endpoint

        Returns:
            The MethodNode that corresponds to the endpoint.
        """
        ranked_methods = []
        for file in files:
            for method in file.methods.values():
                if method.decorator:
                    ranked_methods.append(
                        (method, fuzz.ratio(method.decorator, endpoint_ref))
                    )
        ranked_methods.sort(key=lambda method: method[1], reverse=True)
        return ranked_methods[0][0] if ranked_methods else None

    @abstractmethod
    def extend_file_methods(self, files):   # pragma: no cover
        pass


class PythonParser(BaseParser):
    PY_LANGUAGE = Language(tspython.language())

    def __init__(self):
        """
        Creates queries specific to the Python programming language
        """
        self.parser = Parser(PythonParser.PY_LANGUAGE)
        self.queries = {
            'method_query': PythonParser.PY_LANGUAGE.query(
                """
                    (function_definition
                        name: (identifier) @identifier
                        parameters: (parameters) @parameters
                    ) @method
                """
            ),
            'decorator_query': PythonParser.PY_LANGUAGE.query(
                """
                    (decorated_definition
                        (decorator
                            (call
                                arguments: (argument_list) @decorator))
                            (function_definition
                                name: (identifier) @identifier
                                parameters: (parameters) @parameters
                            )
                        ) @method
                """
            ),
            'call': PythonParser.PY_LANGUAGE.query(
                """(call function: (_) ) @call"""
            ),
            'import': PythonParser.PY_LANGUAGE.query(
                """
                    module_name: (dotted_name) @import
                    name: (dotted_name) @import
                """
            )
        }

    def extend_file_methods(self, files):
        """
        Traverses files to import their methods.
        This is only possible in Python if an an explicit import call is made.

        Args:
            files: The files to traverse
        """  
        file_repository = {file.base.path: file for file in files}
        for file in files:
            tree = self.parser.parse(file.raw_code.encode())
            matches = self.queries['import'].matches(tree.root_node)
            for match in matches:
                for path, other_file in file_repository.items():
                    if match[1]['import'][0].text.decode().replace(".", "/") in path:
                        file.extend(other_file.methods)


class JavaParser(BaseParser):
    JAVA_LANGUAGE = Language(tsjava.language())

    def __init__(self):
        """
        Creates queries specific to the Java programming language
        """
        self.parser = Parser(JavaParser.JAVA_LANGUAGE)
        self.queries = {
            'method_query': JavaParser.JAVA_LANGUAGE.query(
                """
                    (method_declaration
                            name: (identifier) @identifier
                            parameters: (formal_parameters) @parameters
                    ) @method
                """
            ),
            'decorator_query': JavaParser.JAVA_LANGUAGE.query(
                """
                    (method_declaration
                        (modifiers
                            (annotation
                                arguments: (annotation_argument_list) @decorator))
                        name: (identifier) @identifier
                        parameters: (formal_parameters) @parameters
                    ) @method
                """
            ),
            'call': JavaParser.JAVA_LANGUAGE.query(
                """(method_invocation name: (identifier) @call)"""
            ),
            'import': JavaParser.JAVA_LANGUAGE.query(
                """
                    (import_declaration (scoped_identifier) @import)
                """
            ),
            'package': JavaParser.JAVA_LANGUAGE.query(
                """
                    (package_declaration (scoped_identifier) @package)
                """
            )
        }

    def extend_file_methods(self, files):
        """
        Traverses the list of files to import file methods if:
            - the two packages are the same
            - if an explicit import call had been made

        Args:
            files: The files to traverse
        """
        file_repository = {file.base.path: file for file in files}
        for file in files:
            tree = self.parser.parse(file.raw_code.encode())
            matches = self.queries['import'].matches(tree.root_node)
            package = self.queries['package'].matches(tree.root_node)
            for match in matches:
                for path, other_file in file_repository.items():
                    subtree = self.parser.parse(other_file.raw_code.encode())
                    package_match = self.queries['package'].matches(
                        subtree.root_node
                    )
                    if package:
                        for p_match in package_match:
                            if (p_match[1]['package'][0].text.decode() ==
                                    package[0][1]['package'][0].text.decode()):
                                file.extend(other_file.methods)
                    if match[1]['import'][0].text.decode().replace(".", "/") in path:
                        file.extend(other_file.methods)
