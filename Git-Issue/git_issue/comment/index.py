from pathlib import Path
from utils.json_utils import JsonConvert
from git_manager import GitManager


@JsonConvert.register
class IndexEntry(object):
    """description of class"""

    def __init__(self, path: str=None, date: str=None):
        self.path = path
        self.date = date

    def __eq__(self, other):
        if type(other) is not IndexEntry:
            return False

        return self.path == other.path and self.date == other.date

    def __hash__(self):
        return self.path.__hash__() + self.date.__hash__() * 23


@JsonConvert.register
class Index(object):
    """This is an index register of all comments for an issue. It keeps track of all files and their creation date."""

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

    def generate_range(self, volume: int, start_pos:int = 0):
        pos = start_pos
        offset = volume
        no_of_entries = len(self.entries)

        while pos <= no_of_entries:
            yield self.entries[pos:pos + offset]

            pos = pos + offset

    def store_index(self, path):
        loc = Path(path) if path is not None else self._path_to_index
        print(self)
        JsonConvert.ToFile(self, loc)
        gm = GitManager()
        gm.add_to_index([str(loc)])

    @classmethod
    def _generate_index_path(cls, issue_path: Path) -> Path:
        if not issue_path.match("*index.json"):
            return issue_path.joinpath("index.json")

        return issue_path

    @classmethod
    def obtain_index(cls, path):
        index_path = cls._generate_index_path(path)
        
        if (index_path.exists()):
            return JsonConvert.FromFile(index_path)
        else:
            index = Index()
            return index

    def __eq__(self, object: object) -> bool:
        if type(object) is not Index:
            return False

        object: Index = object

        return self.entries == object.entries

    def __hash__(self):
        return self.entries.__hash__()

class IndexEntryInvalidError(Exception):
    pass
