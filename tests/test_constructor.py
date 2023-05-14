from ip_app import create_app


def test_config():
    # simple test for passing a testing configuration
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_index(client):
    # first test to test the response of the main page
    response = client.get('/')
    assert response.data == b'Hi, welcome to the IP services app'
