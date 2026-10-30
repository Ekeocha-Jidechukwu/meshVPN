import subprocess
import time

def run(cmd, namespace=None):
    """Run a shell command, optionally inside a network namespace."""
    if namespace:
        cmd = ['sudo', 'ip', 'netns', 'exec', namespace] + cmd
    return subprocess.run(cmd, capture_output=True, text=True)

def setup_namespaces():
    run(['sudo', 'ip', 'netns', 'add', 'peer1'])
    run(['sudo', 'ip', 'netns', 'add', 'peer2'])

def teardown_namespaces():
    run(['sudo', 'ip', 'netns', 'delete', 'peer1'])
    run(['sudo', 'ip', 'netns', 'delete', 'peer2'])

def test_namespaces_are_isolated():
    setup_namespaces()
    try:
        result = run(['ip', 'addr'], namespace='peer1')
        assert 'lo' in result.stdout
        assert 'eth0' not in result.stdout  # confirms isolation
    finally:
        teardown_namespaces()