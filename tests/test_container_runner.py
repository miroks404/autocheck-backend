from app.checking.container_runner import docker_workspace_mount_args


def test_docker_workspace_mount_uses_named_storage_volume():
    args = docker_workspace_mount_args("/app/storage/submissions/42/workspace")
    assert args == [
        "-v",
        "autocheck_submission_storage:/storage",
        "-w",
        "/storage/submissions/42/workspace",
    ]


def test_docker_workspace_mount_falls_back_for_external_path(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    args = docker_workspace_mount_args(str(workspace))
    assert args[0] == "-v"
    assert args[2] == "-w"
    assert str(workspace) in args[1]
