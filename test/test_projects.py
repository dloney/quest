"""Tests for functions in projects.py"""


import tempfile
import os
import pytest
import shutil

ACTIVE_PROJECT = 'project1'

pytestmark = pytest.mark.usefixtures('reset_projects_dir')


@pytest.fixture()
def init_project_to_add(request):
    base_path = os.path.dirname(os.path.realpath(__file__))
    project_template_dir = os.path.join(base_path, 'files', 'projects_template', 'project1')
    project_dir = os.path.join(base_path, 'files', 'project_to_add')

    def cleanup():
        shutil.rmtree(project_dir, ignore_errors=True)
    cleanup()

    shutil.copytree(project_template_dir, project_dir)

    request.addfinalizer(cleanup)

    return project_dir


@pytest.fixture(params=['project2'])
def test_project(request):
    return request.param


def test_get_projects(api, reset_projects_dir):
    c = api.get_projects()
    assert len(c) == reset_projects_dir['NUMBER_OF_PROJECTS']


def test_default_project(api, ):
    c = api.get_projects()
    assert 'default' in c


def test_new_project(api, reset_projects_dir):
    api.new_project('test')
    c = api.get_projects()
    assert len(c) == reset_projects_dir['NUMBER_OF_PROJECTS'] + 1
    assert 'test' in c


def test_add_project(api, reset_projects_dir, init_project_to_add):
    added_project_name = 'added_test_project'
    api.add_project(added_project_name, init_project_to_add)
    c = api.get_projects()
    assert len(list(c)) == reset_projects_dir['NUMBER_OF_PROJECTS'] + 1
    assert added_project_name in c


def test_delete_project(api, reset_projects_dir, test_project):
    # this test only works if there is more than 1 project
    assert reset_projects_dir['NUMBER_OF_PROJECTS'] > 1

    c = api.delete_project(test_project)
    assert len(c) == reset_projects_dir['NUMBER_OF_PROJECTS'] - 1
    assert test_project not in c


def test_delete_all_projects_default_last(api, reset_projects_dir):
    projects = api.get_projects()
    assert 'default' in projects

    # delete all projects except the default project
    for project in projects:
        if project != 'default':
            api.delete_project(project)

    # ensure that the default project gets re-generated if it is the last project and gets deleted
    c = api.delete_project('default')

    assert len(c) == 1
    assert 'default' in c


def test_delete_all_projects_default_not_last(api, reset_projects_dir, set_active_project):
    # delete all projects except the active project
    for project in api.get_projects():
        if project != ACTIVE_PROJECT:
            api.delete_project(project)

    # ensure that the default project gets re-generated if it is the last project and gets deleted
    c = api.delete_project(ACTIVE_PROJECT)

    assert len(c) == 1
    assert 'default' in c


def test_delete_active_project_with_default(api, reset_projects_dir, set_active_project):
    # this test only works if there are more than 2 projects
    assert reset_projects_dir['NUMBER_OF_PROJECTS'] > 2

    projects = api.get_projects()

    # default project must exist for this test
    assert 'default' in projects

    # active project cannnot be the default project for this test
    assert ACTIVE_PROJECT != 'default'

    c = api.delete_project(ACTIVE_PROJECT)
    assert len(c) == reset_projects_dir['NUMBER_OF_PROJECTS'] - 1
    assert ACTIVE_PROJECT not in c
    new_active_project = api.get_active_project()
    assert new_active_project == 'default'


def test_delete_active_project_without_default(api, reset_projects_dir, set_active_project):
    projects = api.get_projects()

    # default project cannot exist for this test
    if 'default' in projects:
        projects = api.delete_project('default')

    # this test only works if there are more than 2 non default projects projects
    assert len(projects) > 2

    c = api.delete_project(ACTIVE_PROJECT)
    assert len(c) == len(projects) - 1
    assert ACTIVE_PROJECT not in c
    new_active_project = api.get_active_project()
    assert new_active_project != 'default'
    assert new_active_project in c


def test_remove_project():
    pass
    # todo test remove project
    # test case where project is removed and then re-added


def test_set_active_project(api, set_active_project):
    assert api.get_active_project() == 'project1'
    api.set_active_project('default')
    assert api.get_active_project() == 'default'
