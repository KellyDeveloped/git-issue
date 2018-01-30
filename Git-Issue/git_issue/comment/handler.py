from pathlib import Path
from comment import Comment

class CommentHandler(object):
    """description of class"""

    def _generate_comment_path(issue_path:Path, comment_id):
        return issue_path.joinpath(f"comment-{comment_id}.json")

    def _generate_index_path(issue_path:Path):
        return issue_path.joinpath("index.json")

    def _add_to_index(comment):
        pass

    def _get_index():
        pass

    def add_comment(comment):
        pass

    def get_comment(id) -> Comment:
        pass

    def get_comment_range(range) -> [Comment]:
        pass

    def get_all_comments() -> [Comment]:
        pass