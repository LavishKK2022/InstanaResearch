from aioptim.services.parser import PythonParser, JavaParser
import pytest
from unittest.mock import patch, MagicMock
from aioptim.utils.node import Node


@pytest.fixture
def py_raw_code():
    return """
     @app.route("/login")
     def login(user):
        authentateUser()
        if user:
            fetchDetails()
        else:
            signUP()
        return "User is logged in"

    def authenticateUser():
        if self.user_exists:
            return True
        return False

    def signUP():
        return signUpContent()

    @app.route("/get-file")
    def retrieve_file():
        content = findContent()
        return content
    """

@pytest.fixture
def py_ex_raw_code():
    return """
    import src.aioptim.module

    def extraMethod():
        if self.user_exists:
            return True
        return False
    """


@pytest.fixture
def java_raw_code():
    return """
    package com.utils;
    import test.Test;

    public class WebApp{
        @GetMapping("/login")
        public String login(User user){
            boolean isAuthenticated = Authenticate(user);
            if (isAuthenticated){
                return fetchDetails();
            } else {
                return signUp();
            }
        }

        public int fetchDetails(){
            return 1;
        }

        public String signUp(){
            return "User is signed in";
        }

        @GetMapping("/get-file")
        public String getFile(String fileName){
            File file = getContent();
            return file;
        }
    }
    """


@pytest.fixture
def java_ex_raw_code():
    return """
    import util.newAPP;

    public class newAPP{
        public String extraMethod(User user){
            boolean isAuthenticated = Authenticate(user);
            if (isAuthenticated){
                return fetchDetails();
            } else {
                return signUp();
            }
        }
    """

@pytest.fixture
def java_ex2_raw_code():
    return """
    package com.utils;
    import util.oldApp;

    public class newAPP{
        public String extraMethod(User user){
            boolean isAuthenticated = Authenticate(user);
            if (isAuthenticated){
                return fetchDetails();
            } else {
                return signUp();
            }
        }
    """


@pytest.fixture
def py_file_node(py_raw_code):
    file = MagicMock()
    file.raw_code = py_raw_code
    file.methods = {}
    file.base.path = "src/aioptim/module"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file


@pytest.fixture
def java_file_node(java_raw_code):
    file = MagicMock()
    file.raw_code = java_raw_code
    file.methods = {}
    file.base.path = "util/newAPP"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file

@pytest.fixture
def py_ex_file_node(py_ex_raw_code):
    file = MagicMock()
    file.raw_code = py_ex_raw_code
    file.methods = {}
    file.base.path = "src/aioptim/module/main1"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file


@pytest.fixture
def java_ex_file_node(java_ex_raw_code):
    file = MagicMock()
    file.raw_code = java_ex_raw_code
    file.methods = {}
    file.base.path = "src/aioptim/module/main2"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file

@pytest.fixture
def java_ex2_file_node(java_ex2_raw_code):
    file = MagicMock()
    file.raw_code = java_ex2_raw_code
    file.methods = {}
    file.base.path = "src/aioptim/module/main3"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file

@pytest.fixture
def empty_file_node():
    file = MagicMock()
    file.raw_code = """"""
    file.methods = {}
    file.base.path = None
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file


@pytest.fixture
def python_method(py_file_node):
    code = """
     @app.route("/login")
     def login(user):
        authentateUser()
        if user:
            fetchDetails()
        else:
            signUP()
        return "User is logged in"
    """
    return Node.FileNode.MethodNode(
        py_file_node,
        "login",
        "user",
        code,
        "/login"
    )


@pytest.fixture
def java_method(java_file_node):
    code = """
    @GetMapping("/login")
    public String login(User user){
        boolean isAuthenticated = Authenticate(user);
        if (isAuthenticated){
            return fetchDetails();
        } else {
            return signUp();
        }
    }
    """
    return Node.FileNode.MethodNode(
        java_file_node,
        "login",
        "user",
        code,
        "/login"
    )


def test_parse_file_methods(py_file_node, java_file_node):
    PythonParser().parse_file_methods(py_file_node)
    assert len(py_file_node.methods) == 4
    decorator_count = 0
    for _, value in py_file_node.methods.items():
        if value.decorator:
            decorator_count += 1
    assert decorator_count == 2
    JavaParser().parse_file_methods(java_file_node)
    assert len(java_file_node.methods) == 4
    decorator_count = 0
    for _, value in java_file_node.methods.items():
        if value.decorator:
            decorator_count += 1
    assert decorator_count == 2


def test_parse_empty_file_methods(empty_file_node):
    PythonParser().parse_file_methods(empty_file_node)
    assert len(empty_file_node.methods) == 0
    JavaParser().parse_file_methods(empty_file_node)
    assert len(empty_file_node.methods) == 0


def test_parse_method_calls(
        py_file_node,
        java_file_node,
        java_method,
        python_method
):
    PythonParser().parse_file_methods(py_file_node)
    python_result = PythonParser().parse_method_calls(python_method)
    python_result_id = set(res.id for res in python_result)
    assert python_result_id == {'login', 'signUP'}
    JavaParser().parse_file_methods(java_file_node)
    java_result = JavaParser().parse_method_calls(java_method)
    java_result_id = set(res.id for res in java_result)
    assert java_result_id == {'login', 'signUp', 'fetchDetails'}

def test_parse_empty_method_calls():
    assert not JavaParser().parse_method_calls(None)
    assert not PythonParser().parse_method_calls(None)

def test_existing_endpoint_location(py_file_node, java_file_node):
    PythonParser().parse_file_methods(py_file_node)
    JavaParser().parse_file_methods(java_file_node)
    located_py_method = PythonParser().endpoint([py_file_node], "login")
    located_java_method = JavaParser().endpoint([java_file_node], "login")
    assert located_py_method.id == "login"
    assert located_java_method.id == "login"


def test_non_existent_endpoint_location(py_file_node, java_file_node):
    located_py_method = PythonParser().endpoint([py_file_node], "empty")
    located_java_method = JavaParser().endpoint([java_file_node], "empty")
    assert located_py_method is None
    assert located_java_method is None


def test_python_extend_file_methods(py_file_node, py_ex_file_node):
    PythonParser().parse_file_methods(py_ex_file_node)
    PythonParser().parse_file_methods(py_file_node)
    PythonParser().extend_file_methods([py_file_node, py_ex_file_node])
    assert len(py_ex_file_node.methods) == 5


def test_java_extend_file_methods(
        java_file_node,
        java_ex2_file_node,
        java_ex_file_node,
):
    JavaParser().parse_file_methods(java_file_node)
    JavaParser().parse_file_methods(java_ex2_file_node)
    JavaParser().parse_file_methods(java_ex_file_node)
    JavaParser().extend_file_methods(
        [java_ex_file_node, java_ex2_file_node, java_file_node]
    )
    assert len(java_ex2_file_node.methods) == 5
    assert len(java_ex_file_node.methods) == 5
