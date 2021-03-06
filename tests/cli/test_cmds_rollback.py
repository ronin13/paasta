#!/usr/bin/env python
# Copyright 2015 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pytest import raises
from mock import patch, call, Mock
from paasta_tools.cli.cmds.rollback import paasta_rollback
from paasta_tools.cli.cmds.rollback import validate_given_instances


@patch('paasta_tools.cli.cmds.rollback.list_all_instances_for_service', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.validate_given_instances', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.figure_out_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.list_clusters', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.get_git_url', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.mark_for_deployment', autospec=True)
def test_paasta_rollback_mark_for_deployment_simple_invocation(
    mock_mark_for_deployment,
    mock_get_git_url,
    mock_list_clusters,
    mock_figure_out_service_name,
    mock_validate_given_instances,
    mock_list_all_instances_for_service,
):

    fake_args = Mock(
        cluster='cluster1',
        instances='instance1',
        commit='123456'
    )

    mock_get_git_url.return_value = 'git://git.repo'
    mock_figure_out_service_name.return_value = 'fakeservice'
    mock_list_clusters.return_value = ['cluster1', 'cluster2']
    mock_list_all_instances_for_service.return_value = ['instance1', 'instance2']
    mock_validate_given_instances.return_value = [['instance1'], []]

    with raises(SystemExit) as sys_exit:
        paasta_rollback(fake_args)
        assert sys_exit.value_code == 0

    mock_mark_for_deployment.assert_called_once_with(
        git_url=mock_get_git_url.return_value,
        cluster=fake_args.cluster,
        instance=fake_args.instances,
        service=mock_figure_out_service_name.return_value,
        commit=fake_args.commit
    )

    assert mock_mark_for_deployment.call_count == 1


@patch('paasta_tools.cli.cmds.rollback.list_all_instances_for_service', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.validate_given_instances', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.figure_out_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.list_clusters', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.get_git_url', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.mark_for_deployment', autospec=True)
def test_paasta_rollback_mark_for_deployment_wrong_cluster(
    mock_mark_for_deployment,
    mock_get_git_url,
    mock_list_clusters,
    mock_figure_out_service_name,
    mock_validate_given_instances,
    mock_list_all_instances_for_service,
):

    fake_args = Mock(
        cluster='cluster1',
        instances='instance1',
        commit='123456'
    )

    mock_get_git_url.return_value = 'git://git.repo'
    mock_figure_out_service_name.return_value = 'fakeservice'
    mock_list_clusters.return_value = ['cluster0', 'cluster2']
    mock_list_all_instances_for_service.return_value = ['instance1', 'instance2']
    mock_validate_given_instances.return_value = [['instance1'], []]

    with raises(SystemExit) as sys_exit:
        paasta_rollback(fake_args)
        assert sys_exit.value_code == 1

    assert mock_mark_for_deployment.call_count == 0


@patch('paasta_tools.cli.cmds.rollback.list_all_instances_for_service', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.validate_given_instances', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.figure_out_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.list_clusters', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.get_git_url', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.mark_for_deployment', autospec=True)
def test_paasta_rollback_mark_for_deployment_no_instance_arg(
    mock_mark_for_deployment,
    mock_get_git_url,
    mock_list_clusters,
    mock_figure_out_service_name,
    mock_validate_given_instances,
    mock_list_all_instances_for_service,
):

    fake_args = Mock(
        cluster='cluster1',
        commit='123456',
        instances='',
    )

    mock_get_git_url.return_value = 'git://git.repo'
    mock_figure_out_service_name.return_value = 'fakeservice'
    mock_list_clusters.return_value = ['cluster1', 'cluster2']
    mock_list_all_instances_for_service.return_value = ['instance1', 'instance2']
    mock_validate_given_instances.return_value = [['instance1', 'instance2'], []]

    with raises(SystemExit) as sys_exit:
        paasta_rollback(fake_args)
        assert sys_exit.value_code == 0

    expected = [
        call(
            git_url=mock_get_git_url.return_value,
            cluster=fake_args.cluster,
            service=mock_figure_out_service_name.return_value,
            commit=fake_args.commit,
            instance='instance1'
        ),
        call(
            git_url=mock_get_git_url.return_value,
            cluster=fake_args.cluster,
            service=mock_figure_out_service_name.return_value,
            commit=fake_args.commit,
            instance='instance2'
        ),
    ]

    assert expected == mock_mark_for_deployment.mock_calls
    assert mock_mark_for_deployment.call_count == 2


@patch('paasta_tools.cli.cmds.rollback.list_all_instances_for_service', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.validate_given_instances', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.figure_out_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.list_clusters', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.get_git_url', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.mark_for_deployment', autospec=True)
def test_paasta_rollback_mark_for_deployment_wrong_instance_args(
    mock_mark_for_deployment,
    mock_get_git_url,
    mock_list_clusters,
    mock_figure_out_service_name,
    mock_validate_given_instances,
    mock_list_all_instances_for_service,
):

    fake_args = Mock(
        cluster='cluster1',
        commit='123456',
        instances='instance0,not_an_instance'
    )

    mock_get_git_url.return_value = 'git://git.repo'
    mock_figure_out_service_name.return_value = 'fakeservice'
    mock_list_clusters.return_value = ['cluster1', 'cluster2']
    mock_list_all_instances_for_service.return_value = ['instance1', 'instance2']
    mock_validate_given_instances.return_value = [[], ['instance0', 'not_an_instance']]

    with raises(SystemExit) as sys_exit:
        paasta_rollback(fake_args)
        assert sys_exit.value_code == 1

    assert mock_mark_for_deployment.call_count == 0


@patch('paasta_tools.cli.cmds.rollback.list_all_instances_for_service', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.validate_given_instances', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.figure_out_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.list_clusters', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.get_git_url', autospec=True)
@patch('paasta_tools.cli.cmds.rollback.mark_for_deployment', autospec=True)
def test_paasta_rollback_mark_for_deployment_multiple_instance_args(
    mock_mark_for_deployment,
    mock_get_git_url,
    mock_list_clusters,
    mock_figure_out_service_name,
    mock_validate_given_instances,
    mock_list_all_instances_for_service,
):

    fake_args = Mock(
        cluster='cluster1',
        instances='instance1,instance2',
        commit='123456'
    )

    mock_get_git_url.return_value = 'git://git.repo'
    mock_figure_out_service_name.return_value = 'fakeservice'
    mock_list_clusters.return_value = ['cluster1', 'cluster2']
    mock_list_all_instances_for_service.return_value = ['instance1', 'instance2', 'instance3']
    mock_validate_given_instances.return_value = [['instance1', 'instance2'], []]

    with raises(SystemExit) as sys_exit:
        paasta_rollback(fake_args)
        assert sys_exit.value_code == 0

    expected = [
        call(
            git_url=mock_get_git_url.return_value,
            cluster=fake_args.cluster,
            service=mock_figure_out_service_name.return_value,
            commit=fake_args.commit,
            instance='instance1'
        ),
        call(
            git_url=mock_get_git_url.return_value,
            cluster=fake_args.cluster,
            service=mock_figure_out_service_name.return_value,
            commit=fake_args.commit,
            instance='instance2'
        ),
    ]

    mock_mark_for_deployment.assert_has_calls(expected, any_order=True)
    assert mock_mark_for_deployment.call_count == 2


def test_validate_given_instances_no_arg():
    service_instances = ['instance1', 'instance2']
    given_instances = []

    expected_valid = set(['instance1', 'instance2'])
    expected_invalid = set([])

    actual_valid, actual_invalid = validate_given_instances(service_instances, given_instances)

    assert actual_valid == expected_valid
    assert actual_invalid == expected_invalid


def test_validate_given_instances_wrong_arg():
    service_instances = ['instance1', 'instance2']
    given_instances = ['instance0', 'not_an_instance']

    expected_valid = set([])
    expected_invalid = set(['instance0', 'not_an_instance'])

    actual_valid, actual_invalid = validate_given_instances(service_instances, given_instances)

    assert actual_valid == expected_valid
    assert actual_invalid == expected_invalid


def test_validate_given_instances_single_arg():
    service_instances = ['instance1', 'instance2']
    given_instances = ['instance1']

    expected_valid = set(['instance1'])
    expected_invalid = set([])

    actual_valid, actual_invalid = validate_given_instances(service_instances, given_instances)

    assert actual_valid == expected_valid
    assert actual_invalid == expected_invalid


def test_validate_given_instances_multiple_args():
    service_instances = ['instance1', 'instance2', 'instance3']
    given_instances = ['instance1', 'instance2']

    expected_valid = set(['instance1', 'instance2'])
    expected_invalid = set([])

    actual_valid, actual_invalid = validate_given_instances(service_instances, given_instances)

    assert actual_valid == expected_valid
    assert actual_invalid == expected_invalid


def test_validate_given_instances_duplicate_args():
    service_instances = ['instance1', 'instance2', 'instance3']
    given_instances = ['instance1', 'instance1']

    expected_valid = set(['instance1'])
    expected_invalid = set([])

    actual_valid, actual_invalid = validate_given_instances(service_instances, given_instances)

    assert actual_valid == expected_valid
    assert actual_invalid == expected_invalid
