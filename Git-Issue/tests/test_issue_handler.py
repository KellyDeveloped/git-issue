import pytest
import git_issue.issue_handler as handler
from pathlib import Path
from git_issue.tracker import Tracker
from git_issue.issue import Issue
from git_issue.json_utils import JsonConvert

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
    monkeypatch.setattr("git_issue.tracker.Tracker.obtain_tracker", lambda: mt)
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

    monkeypatch.setattr("git_issue.json_utils.JsonConvert.ToFile", MockConvert.ToFile)
    monkeypatch.setattr("git_issue.json_utils.JsonConvert.FromFile", MockConvert.FromFile)
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

def test_tracker_increment(tracker):
    handler._increment_issue_count()
    assert tracker.issue_count == 11

def test_id_generation(tracker):
    assert handler.generate_issue_id() == f"{tracker.ISSUE_IDENTIFIER}-{tracker.issue_count + 1}"

def test_store_issue_stores_file(json, regular_issue):
    handler.store_issue(regular_issue)
    assert json.has_to_file_been_called

def test_store_issue_has_correct_path(monkeypatch, json, regular_issue):
    root = "/tests"
    monkeypatch.setattr("pathlib.Path.cwd", lambda : root)
    handler.store_issue(regular_issue)
    assert json.to_file_path == Path(f"/tests/{regular_issue.id}/issue.json")
    