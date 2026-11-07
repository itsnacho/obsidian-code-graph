"""
AST Parser for Python source files.
Extracts imports, classes, functions, docstrings, and complexity metadata.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ImportInfo:
    """Represents an imported module or symbol."""
    module: str                  # e.g., 'os', 'auth.service', or '' if relative without base
    imported_name: Optional[str] # e.g., 'hash_pwd' in 'from .crypto import hash_pwd'
    alias: Optional[str]         # e.g., 'np' in 'import numpy as np'
    level: int                   # 0 = absolute, 1 = '.', 2 = '..', etc.
    lineno: int


@dataclass
class FunctionInfo:
    """Represents a function or method definition."""
    name: str
    docstring: Optional[str]
    args: List[str]
    return_type: Optional[str]
    lineno: int
    is_async: bool = False


@dataclass
class ClassInfo:
    """Represents a class definition."""
    name: str
    docstring: Optional[str]
    lineno: int
    methods: List[FunctionInfo] = field(default_factory=list)


@dataclass
class ParsedModule:
    """Complete parsed information about a Python source file."""
    file_path: Path
    module_name: str
    docstring: Optional[str]
    is_package_init: bool = False
    imports: List[ImportInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    total_loc: int = 0
    code_loc: int = 0
    parse_error: Optional[str] = None


class ModuleASTVisitor(ast.NodeVisitor):
    """AST visitor that collects imports, classes, and top-level functions."""

    def __init__(self):
        self.imports: List[ImportInfo] = []
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    module=alias.name,
                    imported_name=None,
                    alias=alias.asname,
                    level=0,
                    lineno=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        level = node.level or 0
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    module=module,
                    imported_name=alias.name,
                    alias=alias.asname,
                    level=level,
                    lineno=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_doc = ast.get_docstring(node)
        methods: List[FunctionInfo] = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_function(item))

        self.classes.append(
            ClassInfo(
                name=node.name,
                docstring=class_doc,
                lineno=node.lineno,
                methods=methods,
            )
        )
        # Note: We do not call self.generic_visit(node) to avoid treating methods as top-level functions.

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(self._parse_function(node))
        # Do not recurse into nested functions to keep outline clean

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append(self._parse_function(node))

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        doc = ast.get_docstring(node)
        args_list: List[str] = []

        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args_list.append(arg_str)

        ret_type = ast.unparse(node.returns) if node.returns else None

        return FunctionInfo(
            name=node.name,
            docstring=doc,
            args=args_list,
            return_type=ret_type,
            lineno=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )


class SourceParser:
    """Parses a Python source file using the standard library ast."""

    @staticmethod
    def parse_file(file_path: Path, module_name: str, is_package_init: bool = False) -> ParsedModule:
        """Parses a given file into a ParsedModule structure."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception as e:
                return ParsedModule(
                    file_path=file_path,
                    module_name=module_name,
                    docstring=None,
                    is_package_init=is_package_init,
                    parse_error=f"File read error: {e}",
                )

        lines = content.splitlines()
        total_loc = len(lines)
        code_loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return ParsedModule(
                file_path=file_path,
                module_name=module_name,
                docstring=None,
                is_package_init=is_package_init,
                total_loc=total_loc,
                code_loc=code_loc,
                parse_error=f"SyntaxError at line {e.lineno}: {e.msg}",
            )

        docstring = ast.get_docstring(tree)
        visitor = ModuleASTVisitor()
        visitor.visit(tree)

        return ParsedModule(
            file_path=file_path,
            module_name=module_name,
            docstring=docstring,
            is_package_init=is_package_init,
            imports=visitor.imports,
            classes=visitor.classes,
            functions=visitor.functions,
            total_loc=total_loc,
            code_loc=code_loc,
        )
