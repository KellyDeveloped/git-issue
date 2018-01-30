from pathlib import Path
from utils.json_utils import JsonConvert
from git_manager import GitManager


@JsonConvert.register
class IndexEntry(object):
    """description of class"""

    def __init__(self, path: str=None, date: str=None):
        self.path = path
        self.date = date


@JsonConvert.register
class Index(object):
    """This is an index register of all comments for an issue. It keeps track of all files and their creation date."""

    _path_to_index: Path = None

    def __init__(self, entries: [IndexEntry] = []):
        self.entries = entries

    def has_entry(self, path: Path):
        for entry in self.entries:
            if entry.path == str(path):
                return True

        return False

    def add_entry(self, comment_path: Path, comment):
        issue = IndexEntry(str(comment_path), comment.date)
        self.entries.append(issue)

    def get_entry(self, path: Path) -> IndexEntry:
        for entry in self.entries:
            if entry.path == str(path):
                return entry

        return None

    def get_entries(self) -> [IndexEntry]:
        return self.entries.copy()

    def generate_range(self, volume: int):
        pos = 0
        offset = volume
        no_of_entries = len(self.entries)

        while pos <= no_of_entries:
            yield self.entries[pos:pos + offset]

            pos = pos + offset

    def store_index(self):
        JsonConvert.ToFile(self, self._path_to_index)
        gm = GitManager()
        gm.add_to_index([str(self._path_to_index)])

    @classmethod
    def _generate_index_path(cls, issue_path: Path) -> Path:
        return issue_path.joinpath("index.json")

    @classmethod
    def obtain_index(cls, path):
        cls._path_to_index = cls._generate_index_path(path)
        return JsonConvert.FromFile(cls._path_to_index) if cls._path_to_index.exists() else Index()


class IndexEntryInvalidError(Exception):
    pass
