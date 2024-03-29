from typing import List

import git_issue.comment.index as index
from pathlib import Path
from git_issue.comment.comment import Comment
from git_issue.comment.index import IndexEntry
from git_issue.utils.json_utils import JsonConvert
from git_issue.git_manager import GitManager

class CommentHandler(object):
    """description of class"""

    def __init__(self, issue_path, issue_id):
        if issue_path == None:
            raise AttributeError("Cannot create a comment handler without an issue path.")
        # elif not issue_path.exists():
        #     raise AttributeError("Cannot create a comment handler for an issue that doesn't exist.")

        self.folder_path = self._generate_folder_path(issue_id)
        self.index = index.Index.obtain_index(issue_path)
        self.issue_path = issue_path
        self.issue_id = issue_id

    def _generate_folder_path(self, issue_id):
        return Path(f"{issue_id}/comments")

    def generate_comment_path(self, comment_id):
        return self.folder_path.joinpath(f"{str(comment_id)[:6]}.json")

    def _get_comment(self, entry):
        try:
            return JsonConvert.FromFile(entry.path)
        except FileNotFoundError as err:
            msg = f"An invalid index entry has been found for file \"{err.filename}\"." \
                  f" Please reconstruct the index for {self.folder_path}"
            raise index.IndexEntryInvalidError(msg)

    def _get_list_of_comments(self, entries):
        return [self._get_comment(e) for e in entries]

    def add_comment(self, comment) -> IndexEntry:
        gm = GitManager()

        def gen_paths():
            return [str(self.generate_comment_path(comment.uuid))]

        def action():
            self.index = index.Index.obtain_index(self.issue_path)
            path = self.generate_comment_path(comment.uuid)
            JsonConvert.ToFile(comment, path)
            entry = self.index.add_entry(path, comment)
            self.index.store_index(self.issue_id)
            return entry

        return gm.perform_git_workflow(action, True, gen_paths, "add_comment", self.issue_id)

    def get_comment(self, comment_id) -> Comment:
        entry = self.index.get_entry(self.generate_comment_path(comment_id))
        return self._get_comment(entry)

    def get_comment_range(self, range: int = 10, start_pos: int = 0) -> List[Comment]:
        generator = self.index.generate_range(range, start_pos)
        return self._get_list_of_comments(next(generator))

    def get_all_comments(self) -> [Comment]:
        entries = self.index.get_entries()
        return self._get_list_of_comments(entries)
