import shutil
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.joinpath("../git_issue")))

import os

from comment import Comment
from comment.handler import CommentHandler
from comment.index import Index, IndexEntry
from git_manager import GitManager
from git_utils.merge_utils import CreateConflictResolver, CreateResolutionTool, ConflictInfo, ConflictType, GitMerge, \
    CommentIndexConflictResolver, CommentIndexResolutionTool, DivergenceConflictResolver, DivergenceResolutionTool
from issue.tracker import UUIDTrack, Tracker
from utils.json_utils import JsonConvert

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

def issue_2_with_id_3(issue_2, issue_3):
    issue_2.id = issue_3.id
    return issue_2

@pytest.fixture
def original_index_entry():
    return Index([IndexEntry("594832.json", "2018-02-25T22:33:56.04040"),
                  IndexEntry("894754.json", "2018-02-25T22:33:58.00000")])

@pytest.fixture
def conflicting_index_entry():
    return Index([IndexEntry("239171.json", "2018-02-25T22:50:02.00111"),
                  IndexEntry("345234.json", "2018-02-25T22:33:56.97968")])

@pytest.fixture
def sorted_comment_index():
    return Index([IndexEntry("594832.json", "2018-02-25T22:33:56.04040"),
                  IndexEntry("345234.json", "2018-02-25T22:33:56.97968"),
                  IndexEntry("894754.json", "2018-02-25T22:33:58.00000"),
                  IndexEntry("239171.json", "2018-02-25T22:50:02.00111")])

@pytest.fixture
def comment_index_conflict(original_index_entry, conflicting_index_entry):
    return  ConflictInfo("fake_path", [original_index_entry, conflicting_index_entry])

@pytest.fixture(scope='session')
def first_repo_path():
    return "first-repo"


@pytest.fixture(scope='session')
def second_repo_path():
    return "second-repo"


@pytest.fixture
def first_repo(tmpdir, first_repo_path):
    repo = git.Repo.init(tmpdir.mkdir(first_repo_path))

    fake_file_dir = Path(repo.working_dir + "/fake-file.pla")
    open(fake_file_dir, 'w').close()
    repo.index.add([str(fake_file_dir)])
    repo.index.commit("Blah")

    os.chdir(repo.working_dir)
    gm = GitManager()
    setattr(gm, "get_choice_from_user", lambda x: True)
    gm.load_issue_branch()

    return repo

@pytest.fixture
def second_repo(first_repo):
    path = Path(first_repo.working_dir).parent.joinpath("second_repo")
    git.Repo.clone_from(first_repo.working_dir, path)
    repo = git.Repo(str(path))
    repo.create_remote("other", f"{first_repo.git_dir}")
    first_repo.create_remote("other", f"{repo.git_dir}")

    return repo


def test_create_resolver(issue_1: Issue, issue_2: Issue, monkeypatch, first_repo: git.Repo):
    issue_2.id = "ISSUE-1" # Cause a conflict with the ID's

    issues = [ConflictInfo("Fake_Path", [issue_1, issue_2])]

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
    issues = [issue_1, issue_2]

    os.chdir(first_repo.working_dir)
    monkeypatch.setattr("git_manager.GitManager.get_choice_from_user", lambda x, y: True)
    monkeypatch.setattr("builtins.input", lambda x: 'Y')

    uuids = [UUIDTrack(issue_1.uuid, issue_1.id), UUIDTrack(issue_2.uuid, issue_2.id)]

    resolution = CreateResolutionTool(issues, Tracker(len(uuids), uuids))

    resolution.resolve()

    assert issue_1_path.exists()
    assert issue_2_path.exists()

    result_1 = handler.get_issue_from_issue_id(issues[0].id)
    result_2 = handler.get_issue_from_issue_id(issues[1].id)

    assert issues[0] == result_1
    assert issues[1] == result_2

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

def test_comment_index_resolver(comment_index_conflict, sorted_comment_index):
    resolver = CommentIndexConflictResolver()
    resolver.conflicts = [conflict for conflict in comment_index_conflict.conflicts]
    resolver.path = "fake_path"

    result = resolver.generate_resolution()
    assert sorted_comment_index == result.index

def test_comment_index_resolution(sorted_comment_index, first_repo):
    os.chdir(first_repo.working_dir)

    path = Path("ISSUE-1/index.json")
    resolution = CommentIndexResolutionTool(sorted_comment_index, path)
    resolution.resolve()

    index = Index.obtain_index(path)
    assert index == sorted_comment_index

def test_produce_divergence_resolver(issue_1, issue_2, issue_3, first_repo):
    resolved_issues = [issue_1, issue_2, issue_3]
    resolved_tracker = Tracker()

    for issue in resolved_issues:
        resolved_tracker.track_or_update_uuid(issue.uuid, issue.id)

    issue_2_json = JsonConvert.ToJSON(issue_2)
    issue_2_copy = JsonConvert.FromJSON(issue_2_json)
    issue_2_copy.uuid = 53368803138698180295652887974160049016

    conflict = ConflictInfo(IssueHandler().get_issue_path(issue_2), [issue_2, issue_2, issue_2_copy])

    merger = GitMerge(first_repo)
    resolver = merger.produce_create_edit_divergence_resolver([conflict], resolved_issues, resolved_tracker)
    assert resolved_issues == resolver.resolved_conflicts and resolved_tracker == resolver.resolved_tracker
    assert [(issue_2, issue_2_copy)] == resolver.diverged_issues

def test_divergence_resolver(issue_1, issue_2, issue_3, monkeypatch):
    resolved_issues = [issue_1, issue_2, issue_3]
    resolved_tracker = Tracker()

    summary_edit = "This edit resolves the create-edit-divergence"
    monkeypatch.setattr("builtins.input", lambda x: summary_edit)

    for issue in resolved_issues:
        resolved_tracker.track_or_update_uuid(issue.uuid, issue.id)

    issue_3_json = JsonConvert.ToJSON(issue_3)
    issue_3_copy = JsonConvert.FromJSON(issue_3_json)
    issue_3_copy.summary = "This is the edited field for the create-edit-divergence"
    issue_3_copy.id = issue_2.id

    expected = JsonConvert.FromJSON(issue_3_json)
    expected.summary = summary_edit

    resolver = DivergenceConflictResolver()
    resolver.resolved_tracker = resolved_tracker
    resolver.resolved_conflicts = resolved_issues
    resolver.diverged_issues = [(issue_3, issue_3_copy)]

    resolution = resolver.generate_resolution()
    assert [issue_3, expected] == resolution.resolved_issues

def test_divergence_resolution(issue_3, first_repo, monkeypatch):
    os.chdir(first_repo.working_dir)
    monkeypatch.setattr("builtins.input", lambda x: 'Y')

    resolution = DivergenceResolutionTool([issue_3])
    resolution.resolve()

    handler = IssueHandler()
    result = handler.get_issue_from_issue_id(issue_3.id)

    assert issue_3 == result

def test_unmerged_conflicts(issue_1: Issue, issue_2: Issue, issue_3: Issue, first_repo: git.Repo, second_repo: git.Repo,
                            monkeypatch):
    # Create, Create-Edit-Divergence, Comment-Index, Manual
    issue_2_json = JsonConvert.ToJSON(issue_2)
    issue_2_copy = JsonConvert.FromJSON(issue_2_json)
    issue_2_copy.summary = "Edited Summary"

    monkeypatch.setattr("git_manager.GitManager.get_choice_from_user", lambda x, y: True)
    monkeypatch.setattr("builtins.input", lambda x: 'Y')

    def merge(repo):
        try:
            repo.git.checkout("issue")
            repo.git.pull("--allow-unrelated-histories", "other", GitManager.ISSUE_BRANCH)
        except:
            pass

        merger = GitMerge(repo)
        return merger.parse_unmerged_conflicts()

    # Set up first repo for Create conflict
    os.chdir(first_repo.working_dir)
    handler = IssueHandler()
    handler.store_issue(issue_2, "test", generate_id=True)

    # Set up second repo for Create conflict
    os.chdir(second_repo.working_dir)
    handler = IssueHandler()
    handler.store_issue(issue_1, "test", generate_id=True)

    result = merge(second_repo)
    expected = [ConflictInfo("ISSUE-1/issue.json", [issue_1, issue_2])]
    assert expected == result
    resolver = GitMerge(second_repo).produce_create_resolver(result)
    resolution = resolver.generate_resolution()
    resolution.resolve()

    # Set up first repo for divergence conflict
    os.chdir(first_repo.working_dir)
    handler = IssueHandler()
    issue_2_copy.id = issue_1.id
    handler.store_issue(issue_2_copy, "test")

    os.chdir(second_repo.working_dir)
    result = merge(second_repo)
    expected = [ConflictInfo("ISSUE-1/issue.json", [issue_2, issue_1, issue_2_copy])]
    assert expected == result
    resolver = GitMerge(second_repo).produce_create_edit_divergence_resolver(result, resolution.resolved_issues, resolution.tracker)
    resolver.generate_resolution().resolve()

    # Comment
    os.chdir(first_repo.working_dir)
    handler = IssueHandler()
    comment_handler = CommentHandler(handler.get_issue_path(issue_1), issue_1.id)
    first_comment = Comment("first repo")
    first_entry = comment_handler.add_comment(first_comment)

    # Comment
    # os.chdir(second_repo.working_dir)
    # handler = IssueHandler()
    # comment_handler = CommentHandler(handler.get_issue_path(issue_1), issue_1.id)
    # second_comment = Comment("second repo")
    # second_entry = comment_handler.add_comment(second_comment)
    #
    # result = merge(second_repo)
    # expected = [ConflictInfo("ISSUE-1/index.json", [Index([second_entry]), Index([first_entry])])]
    #
    # assert expected == result
    # resolver = GitMerge(second_repo).produce_comment_index_resolver("ISSUE-1/index.json", result)
    # resolver.generate_resolution().resolve()

    # Edit conflict
    issue_1.id = "ISSUE-10" # Just so we don't need to work out the ID
    issue_1_json = JsonConvert.ToJSON(issue_1)
    issue_1_first_repo = JsonConvert.FromJSON(issue_1_json)
    issue_1_second_repo = JsonConvert.FromJSON(issue_1_json)
    issue_1_first_repo.summary = "First Repo"
    issue_1_second_repo.summary = "Second Repo"

    # Set up both repos with the issue that will be used as a conflict
    os.chdir(first_repo.working_dir)
    handler = IssueHandler()
    handler.store_issue(issue_1, "test")
    os.chdir(second_repo.working_dir)
    result = merge(second_repo)

    # Edit first repo
    os.chdir(first_repo.working_dir)
    handler.store_issue(issue_1_first_repo, "test")

    # Edit second repo
    os.chdir(second_repo.working_dir)
    handler = IssueHandler()
    handler.store_issue(issue_1_second_repo, "issue 10 edit")
    result = merge(second_repo)

    expected = [ConflictInfo("ISSUE-10/issue.json", [issue_1, issue_1_second_repo, issue_1_first_repo])]
    assert expected == result