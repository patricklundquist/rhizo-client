import json
import random
from rhizo.config import load_config
from rhizo.resources import ResourceClient, ApiError


# test the resource client can write a file and read it back again
def test_resource_client_read_write_file():
    for new_version in [False]:
        config = load_config('local.yaml')
        resource_client = ResourceClient(config)
        contents = 'This is a test.\n%d.\n' % random.randint(1, 1000)
        resource_client.write_file(config.server_test_path + '/test.txt', contents, new_version = new_version)
        server_contents = resource_client.read_file(config.server_test_path + '/test.txt').decode()
        assert contents == server_contents


# test the resource client can write a file and read it back again
def test_resource_client_read_write_large_file():
    for binary in [False, True]:
        config = load_config('local.yaml')
        resource_client = ResourceClient(config)
        if binary:
            contents = bytearray(list(range(256)) * 100)
        else:
            contents = ('This is a test.\n%d.\n' % random.randint(1, 1000)) * 1000
        resource_client.write_file(config.server_test_path + '/testLarge.txt', contents)
        data = resource_client.read_file(config.server_test_path + '/testLarge.txt')
        if not binary:
            data = data.decode()
        assert contents == data


# test the resource client can write a file and read it back again
def test_resource_client_file_exists():
    config = load_config('local.yaml')
    resource_client = ResourceClient(config)
    assert resource_client.file_exists(config.server_test_path + '/test.txt')
    assert not resource_client.file_exists(config.server_test_path + '/test12345.txt')


# test the resource client can create multiple levels of folders at once
def test_resource_client_create_folder():
    config = load_config('local.yaml')
    resource_client = ResourceClient(config)
    path = config.server_test_path + '/folder%06d/folder%06d' % (random.randint(1, 999999), random.randint(1, 999999))
    resource_client.create_folder(path)
    assert resource_client.file_exists(path) == True


# test that the resource client can update and read a sequence value
def test_resource_client_read_write_sequence():
    for new_version in [False, False]:
        config = load_config('local.yaml')
        resource_client = ResourceClient(config)
        resource_client.write_file(config.server_test_path + '/test-text-seq', 'ok', new_version = new_version)
        assert 'ok' == resource_client.read_file(config.server_test_path + '/test-text-seq').decode()
        resource_client.write_file(config.server_test_path + '/test-text-seq', 'test', new_version = new_version)
        assert 'test' == resource_client.read_file(config.server_test_path + '/test-text-seq').decode()


# test that the resource client can be used to send a message
def test_resource_client_send_message():

    # prepare to send messages
    config = load_config('local.yaml')
    resource_client = ResourceClient(config)
    params = {
        'abc': 'test',
        'xyz': 777,
    }

    # check sending message to valid testing folder
    resource_client.send_message(config.server_test_path, 'testMessage', params)

    # check non-existent path
    try:
        resource_client.send_message('/path/does/not/exist', 'testMessage', params)
        assert False
    except ApiError as e:
        assert e.status == 404

    # check non-authorized path
    try:
        resource_client.send_message('/system', 'testMessage', params)
        assert False
    except ApiError as e:
        assert e.status == 403


# if run as a top-level script
if __name__ == '__main__':
    test_resource_client_read_write_file()
