"""
This component extracts and updates teh files in the 
linked GitHub repository.

[2] https://stackoverflow.com/a/46897418
    Stack Overflow: Andy Fraley
    "How to checkout to a new branch with Pygithub?"
"""

from __future__ import annotations
from github import Github, Auth
from pathlib import Path
from dataclasses import dataclass
from rapidfuzz import fuzz
import time
from aioptim.utils.node import Node


@dataclass
class GithubProcessor:
    """ Wrapper around the PyGitHub object """

    access_token: str
    repository_name: str
    default_branch: str

    def __post_init__(self):
        """
        Sets up the processor and locates the file with
        read and write permissions.

        This utilises a fuzzy matching approach.

        Raises:
            FileNotFoundError: Repository with read/write permissions not found
        """
        self.github = Github(auth=Auth.Token(self.access_token))
        repositories = self.github.get_user().get_repos()
        matched_repositories = sorted(
            repositories,
            reverse=True,
            key=lambda repo: fuzz.ratio(repo.name, self.repository_name)
        )
        if (
            matched_repositories
            and matched_repositories[0].permissions.pull
            and matched_repositories[0].permissions.push
        ):
            self.repository_path = matched_repositories[0].full_name
        else:
            raise FileNotFoundError(
                "Repository with read & write permissions not found"
            )

    def __getitem__(self, extension):
        """
        Retrieves files with a specific type of extension.

        Args:
            extension: The file extension to search for

        Returns:
            A list of files of the same extension type
        """
        files = []
        repository = self.github.get_repo(self.repository_path)
        contents = repository.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(
                    repository.get_contents(file_content.path))
            elif Path(file_content.path).suffix == "." + extension:
                files.append(Node.FileNode(file_content))
        return files

    def update_file(self, method_node, new_code):
        """
        Updates the file in the remote repository.
        This first creates a new branch [2], and then pushes code on that branch.

        Args:
            method_node: The original method node, which contains references to the base file
            new_code: The code to relpace the method node's old code
        """
        if not new_code:
            return
        new_file = method_node.parent.raw_code.replace(
            method_node.method, new_code)
        repository = self.github.get_repo(self.repository_path)
        contents = repository.get_contents(
            method_node.parent.base.path, ref=repository.default_branch)
        source_branch = repository.get_branch(repository.default_branch)
        target_branch = time.strftime("%Y-%m-%d/%H-%M-%S")
        repository.create_git_ref(
            ref='refs/heads/' + target_branch, sha=source_branch.commit.sha
        )
        repository.update_file(
            path=contents.path,
            message="IBM Monitoring Service: UPDATE",
            content=new_file,
            sha=contents.sha,
            branch=target_branch
        )
