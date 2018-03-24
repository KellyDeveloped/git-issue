import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("..")))
import pytest
import git
import os
import git_issue.issue.handler as handler
from git_issue.issue.handler import IssueHandler
from git_issue.git_manager import GitManager
from git_issue.issue.tracker import Tracker
from git_issue.issue.issue import Issue
from git_issue.utils.json_utils import JsonConvert

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

@pytest.fixture
def tracker(monkeypatch):
    class MockTracker(Tracker):

        def __init__(self, issue_count=0):
            self.issue_count = 10
            self.tracked_uuids = []

        def store_tracker(self):
            pass

        @classmethod
        def obtain_tracker(cls):
            return MockTracker()

    mt = MockTracker()
    monkeypatch.setattr("git_issue.issue.tracker.Tracker.obtain_tracker", lambda: mt)
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

    monkeypatch.setattr("git_issue.utils.json_utils.JsonConvert.ToFile", MockConvert.ToFile)
    monkeypatch.setattr("git_issue.utils.json_utils.JsonConvert.FromFile", MockConvert.FromFile)
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
    
    new_dir = Path(dir).joinpath(f"{issue.id}/issue.json")
    JsonConvert.ToFile(issue, new_dir)

    return new_dir

@pytest.fixture
def test_repo(tmpdir):
    repo = git.Repo.init(tmpdir.mkdir("test_repo"))

    fake_file_dir = Path(repo.working_dir + "/fake-file.pla")
    open(fake_file_dir, 'w').close()
    repo.index.add([str(fake_file_dir)])
    repo.index.commit("Blah")

    os.chdir(repo.working_dir)
    gm = GitManager()
    setattr(gm, "get_choice_from_user", lambda x: True)
    gm.load_issue_branch()

    return repo

def test_tracker_increment(tracker):
    tracker.increment_issue_count()
    assert tracker.issue_count == 11

def test_id_generation(tracker):
    assert handler.generate_issue_id() == f"{tracker.ISSUE_IDENTIFIER}-{tracker.issue_count + 1}"

def test_store_issue_stores_file(regular_issue, test_repo):
    ih = IssueHandler()
    ih.store_issue(regular_issue, None, True)
    result = ih.get_issue_from_issue_id(regular_issue.id)
    regular_issue.id = "ISSUE-11" # 11 because tracker is mocked to have 10 entries

    assert regular_issue == result

def test_store_issue_has_correct_path(regular_issue, test_repo):
    root = f"{test_repo.working_dir}/issue"
    ih = IssueHandler()
    ih.store_issue(regular_issue, None)
    gm = GitManager()
    gm.load_issue_branch()
    assert Path(f"{root}/{regular_issue.id}/issue.json").exists()

def test_get_issue(monkeypatch, tmpdir, regular_issue):
    dir = create_tmp_file(tmpdir, regular_issue)

    monkeypatch.setattr("pathlib.Path.joinpath", lambda x, y: Path(dir))

    result = handler.get_issue(regular_issue.id)
    assert regular_issue.id == result.id


def test_get_all_issues(monkeypatch, tmpdir, regular_issue, test_repo):
    expected = [regular_issue, Issue("ISSUE-NA")]

    dirs = []
    tmpdir.mkdir("/issue")
    root = f"{test_repo.working_dir}/issue"
    dirs.append(create_tmp_file(root, expected[0]))
    dirs.append(create_tmp_file(root, expected[1]))
    
    print(dirs)
    
    result = handler.get_all_issues()

    expected.sort(key=lambda x: x.id)
    result.sort(key=lambda x: x.id)
    
    assert len(expected) == len(result)
    assert expected[0].id == result[0].id and expected[1].id == result[1].id