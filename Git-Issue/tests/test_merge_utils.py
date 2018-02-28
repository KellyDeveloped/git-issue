import sys
from pathlib import Path

import os

from comment.index import Index, IndexEntry
from git_utils.merge_utils import CreateConflictResolver, CreateResolutionTool, ConflictInfo, ConflictType, GitMerge, \
    CommentIndexConflictResolver
from issue.tracker import UUIDTrack, Tracker

sys.path.append(str(Path(__file__).parent.joinpath("../git_issue")))

import pytest

import git
from issue.handler import IssueHandler
from gituser import GitUser
from issue.issue import Issue


@pytest.fixture
def issue_1():
    issue = Issue()
    issue.id = "ISSUE-1"
    issue.date = "2018-02-25T22:33:50.04040"
    issue.uuid = 125118048431737826035520921347116368363
    issue.assignee = GitUser("liam", "liam@test.com")
    issue.reporter = GitUser("bob", "bob@test.com")
    issue.description = "description-of-issue-1"
    issue.summary = "summary-of-issue-1"
    return issue


@pytest.fixture
def issue_2():
    issue = Issue()
    issue.id = "ISSUE-2"
    issue.uuid = 219614693126630377445621689697662132760
    issue.date = "2018-02-25T22:33:56.97968"
    issue.assignee = GitUser("liam", "kelly@test.com")
    issue.reporter = GitUser("bob", "atkey@test.com")
    issue.description = "description-of-issue-2"
    issue.summary = "summary-of-issue-2"
    return issue


@pytest.fixture
def issue_3():
    issue = Issue()
    issue.id = "ISSUE-3"
    issue.uuid = 53368803138698180295652887974160049016
    issue.date = "2018-02-25T22:33:58.00000"
    issue.description = "description-of-issue-3"
    issue.summary = "summary-of-issue-3"
    return issue

@pytest.fixture
def original_index_entry():
    return Index([IndexEntry("594832.json", "2018-02-25T22:33:56.04040"),
                  IndexEntry("894754.json", "2018-02-25T22:33:58.00000")])

@pytest.fixture
def conflicting_index_entry():
    return Index([IndexEntry("345234.json", "2018-02-25T22:33:56.97968"),
           IndexEntry("239171.json", "2018-02-25T22:33:58.00000")])

@pytest.fixture
def comment_index_conflict(original_index_entry, conflicting_index_entry):
    return  ConflictInfo("fake_path", [original_index_entry, conflicting_index_entry])

@pytest.fixture(scope='session')
def first_repo_path():
    return "first-repo"


@pytest.fixture(scope='session')
def second_repo_path():
    return "second-repo"


@pytest.fixture(scope='session')
def first_repo(tmpdir_factory, first_repo_path):
    return git.Repo.init(tmpdir_factory.mktemp(first_repo_path))


@pytest.fixture(scope='session')
def second_repo(tmpdir_factory, first_repo_path, second_repo_path):
    repo = git.Repo.init(tmpdir_factory.mktemp(second_repo_path))
    repo.create_remote("local", f"../{first_repo_path}")

    return repo


def test_create_resolver(issue_1: Issue, issue_2: Issue, monkeypatch, first_repo: git.Repo):
    issue_2.id = "ISSUE-1" # Cause a conflict with the ID's

    issues = [issue_1, issue_2]

    os.chdir(first_repo.working_dir)
    monkeypatch.setattr("git_manager.GitManager.get_choice_from_user", lambda x, y: True)

    resolver = CreateConflictResolver()
    resolver.conflicts = issues
    resolution = resolver.generate_resolution()

    found = False
    for issue in resolution.resolved_issues:
        if issue.id == "ISSUE-2":
            found = True

    assert found


def test_create_resolution(issue_1: Issue, issue_2: Issue, monkeypatch, first_repo: git.Repo):
    handler = IssueHandler()

    issue_1_path = handler.get_issue_path(issue_1)
    issue_2_path = handler.get_issue_path(issue_2)
    issues = [(issue_1, str(issue_1_path)), (issue_2, str(issue_2_path))]

    os.chdir(first_repo.working_dir)
    monkeypatch.setattr("git_manager.GitManager.get_choice_from_user", lambda x, y: True)

    uuids = [UUIDTrack(issue_1.uuid, issue_1.id), UUIDTrack(issue_2.uuid, issue_2.id)]

    resolution = CreateResolutionTool(issues, Tracker(len(uuids), uuids))

    resolution.resolve()

    assert issue_1_path.exists()
    assert issue_2_path.exists()

    result_1 = handler.get_issue_from_issue_id(issues[0][0].id)
    result_2 = handler.get_issue_from_issue_id(issues[1][0].id)

    assert result_1 == issues[0][0]
    assert result_2 == issues[1][0]

def test_produce_create_resolver(issue_1: Issue, issue_2: Issue, first_repo):
    conflict = ConflictInfo("fake_path", [issue_1, issue_2])

    # Not what we're testing in this unit, but it's imperative that we know
    # what we're dealing with is a create conflict
    assert conflict.type == ConflictType.CREATE

    merger = GitMerge(first_repo)
    result = merger.produce_create_resolver([conflict])

    assert 1 == len(result.conflicts) and 2 == len(result.conflicts[0].conflicts)
    assert 2 == len(result.tracker.tracked_uuids) and 2 == result.tracker.issue_count

    assert conflict == result.conflicts[0]
    assert [UUIDTrack(issue.uuid, issue.id) for issue in conflict.conflicts]\
        == result.tracker.tracked_uuids

def test_produce_comment_index_resolver(comment_index_conflict, first_repo):
    merger = GitMerge(first_repo)
    resolver = merger.produce_comment_index_resolver(comment_index_conflict.path, [comment_index_conflict])
    assert [comment_index_conflict] == resolver.conflicts and comment_index_conflict.path == resolver.path

def test_comment_index_resolver(comment_index_conflict, original_index_entry, conflicting_index_entry):
    resolver = CommentIndexConflictResolver()
    resolver.conflicts = [conflict for conflict in comment_index_conflict.conflicts]
    resolver.path = "fake_path"

    expected_entries = original_index_entry.entries + conflicting_index_entry.entries
    expected_entries.sort(key=lambda x: x.date)

    result = resolver.generate_resolution()
    assert expected_entries == result.index.entries

