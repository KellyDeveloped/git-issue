import sys
from pathlib import Path
from unittest.mock import MagicMock
sys.path.append(str(Path(__file__).parent.joinpath("../git_issue")))
import pytest
import inspect
import issue_handler as handler
from git_manager import GitManager
from tracker import Tracker
from issue import Issue
from utils.json_utils import JsonConvert

@pytest.fixture
def tracker(monkeypatch):
    class MockTracker(Tracker):

        def __init__(self, issue_count=0):
            self.issue_count = 10

        def store_tracker(self):
            pass

        @classmethod
        def obtain_tracker(cls):
            return MockTracker()

    mt = MockTracker()
    monkeypatch.setattr("tracker.Tracker.obtain_tracker", lambda: mt)
    return mt

@pytest.fixture
def json(monkeypatch):
    class MockConvert(object):

        has_to_file_been_called = False
        has_from_file_been_called = False
        to_file_path = None

        @classmethod
        def ToFile(cls, obj, path=None):
            cls.has_to_file_been_called = True
            cls.to_file_path = path

        @classmethod
        def FromFile(cls, filepath):
            cls.has_from_file_been_called = True

    monkeypatch.setattr("utils.json_utils.JsonConvert.ToFile", MockConvert.ToFile)
    monkeypatch.setattr("utils.json_utils.JsonConvert.FromFile", MockConvert.FromFile)
    return MockConvert()

@pytest.fixture
def regular_issue(tracker):
    issue = Issue()
    issue.id = "ISSUE-30"
    issue.assignee = "liam"
    issue.reporter = "bob"
    issue.description = "description"
    issue.summary = "summary"
    return issue

def create_tmp_file(dir, issue):
    class FakeParent():
        def exists(any=None):
            return True
    
    new_dir = dir.mkdir(issue.id).join("issue.json")
    new_dir.parent = FakeParent()
    JsonConvert.ToFile(issue, new_dir)

    return new_dir

def mock_git():
    def fake_method(*nargs):
        return

    gm = GitManager()
    methods = inspect.getmembers(gm, predicate=inspect.ismethod)

    for m in methods:
        setattr(GitManager, m[0], fake_method)


def test_tracker_increment(tracker):
    handler._increment_issue_count()
    assert tracker.issue_count == 11

def test_id_generation(tracker):
    assert handler.generate_issue_id() == f"{tracker.ISSUE_IDENTIFIER}-{tracker.issue_count + 1}"

def test_store_issue_stores_file(json, regular_issue):
    mock_git()
    handler.store_issue(regular_issue, None)
    assert json.has_to_file_been_called

def test_store_issue_has_correct_path(monkeypatch, json, regular_issue):
    mock_git()
    root = "/tests"
    monkeypatch.setattr("pathlib.Path.cwd", lambda : Path(root))
    handler.store_issue(regular_issue, None)
    assert json.to_file_path == Path(f"/tests/{regular_issue.id}/issue.json")

def test_get_issue(monkeypatch, tmpdir, regular_issue):  
    dir = create_tmp_file(tmpdir, regular_issue)

    mock_git()
    monkeypatch.setattr("pathlib.Path.joinpath", lambda x, y : dir)

    result = handler.get_issue(regular_issue.id)
    assert regular_issue.id == result.id


def test_get_all_issues(monkeypatch, tmpdir, regular_issue):
    expected = [regular_issue, Issue("ISSUE-NA")]

    mock_git()

    dirs = []
    dirs.append(create_tmp_file(tmpdir, expected[0]))
    dirs.append(create_tmp_file(tmpdir, expected[1]))
    
    print(dirs)
    monkeypatch.setattr("pathlib.Path.cwd", lambda : Path(tmpdir))
    
    result = handler.get_all_issues()

    expected.sort(key=lambda x: x.id)
    result.sort(key=lambda x: x.id)
    
    assert len(expected) == len(result)
    assert expected[0].id == result[0].id and expected[1].id == result[1].id