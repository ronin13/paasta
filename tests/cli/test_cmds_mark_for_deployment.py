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

from mock import patch
from mock import ANY
from pytest import raises

from paasta_tools.cli.cmds import mark_for_deployment


class fake_args:
    clusterinstance = 'cluster.instance'
    service = 'test_service'
    git_url = 'git://false.repo/services/test_services'
    commit = 'fake-hash'


@patch('paasta_tools.cli.cmds.mark_for_deployment.validate_service_name', autospec=True)
@patch('paasta_tools.cli.cmds.mark_for_deployment.mark_for_deployment', autospec=True)
def test_paasta_mark_for_deployment_acts_like_main(
    mock_mark_for_deployment,
    mock_validate_service_name,
):
    mock_mark_for_deployment.return_value = 42
    with raises(SystemExit) as sys_exit:
        mark_for_deployment.paasta_mark_for_deployment(fake_args)
    mock_mark_for_deployment.assert_called_once_with(
        service='test_service',
        instance='instance',
        cluster='cluster',
        commit='fake-hash',
        git_url='git://false.repo/services/test_services',
    )

    assert mock_validate_service_name.called
    assert sys_exit.value.code == 42


@patch('paasta_tools.remote_git.create_remote_refs', autospec=True)
def test_mark_for_deployment_happy(mock_create_remote_refs):
    actual = mark_for_deployment.mark_for_deployment(
        git_url='fake_git_url',
        cluster='fake_cluster',
        instance='fake_instance',
        service='fake_service',
        commit='fake_commit',
    )
    assert actual == 0
    mock_create_remote_refs.assert_called_once_with(
        git_url='fake_git_url',
        ref_mutator=ANY,
        force=True,
    )


@patch('paasta_tools.remote_git.create_remote_refs', autospec=True)
def test_mark_for_deployment_sad(mock_create_remote_refs):
    mock_create_remote_refs.side_effect = Exception('something bad')
    actual = mark_for_deployment.mark_for_deployment(
        git_url='fake_git_url',
        cluster='fake_cluster',
        instance='fake_instance',
        service='fake_service',
        commit='fake_commit',
    )
    assert actual == 1
    mock_create_remote_refs.assert_called_once_with(
        git_url='fake_git_url',
        ref_mutator=ANY,
        force=True,
    )
