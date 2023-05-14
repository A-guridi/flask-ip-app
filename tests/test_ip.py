import pytest
from ip_app.model import get_db
import xml.etree.ElementTree as ET


@pytest.mark.parametrize(('ipAddress', 'abuseCategories', 'api_key'), (
    ('1.2.3.4', [1, 2], 'api-key1'),
    ('10.42.3.125', [1], 'api-key1'),
    ('23.45.2.234', [1, 2, 3], 'apikey2'),
    ('10.42.3.125', [1, 2], 'api-key1'),
))
def test_report_ip(client, app, ipAddress:str, abuseCategories:list, api_key:str):
    # test to upload some IPs to the system and update 1 after, checking after each upload that they are saved in the DB
    response = client.post(
        '/ip_security/report_ip',
        headers={'Content-Type': 'application/json', 'api_key': api_key },
        json={'ipAddress': ipAddress, 'abuseCategories': list(abuseCategories)}
    )
    assert 201 == response.status_code
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM blocked_ips').fetchone()[0]
        assert count == 1



@pytest.mark.parametrize(('ipAddress', 'abuseCategories', 'api_key', 'status'), (
    ('255.256.0.0', [1, 2], 'api-key1', 400),            # wrong ip add
    ('10.42.3.125', [1], 'apikey1', 403),                # wrong api-key
    ('23.45.2.234', [3, 4, 5], 'apikey2', 400),          # wrong report types
    ('23.45.2.234', [1], '', 403),                       # no api key provided
))
def test_report_ip_wrong(client, ipAddress:str, abuseCategories:list, api_key:str, status:int):
    # test to upload 4 different wrong examples and catch the errors returned by the system
    response = client.post(
        '/ip_security/report_ip',
        headers={'Content-Type': 'application/json', 'api_key': api_key},
        json={'ipAddress': ipAddress, 'abuseCategories': list(abuseCategories)}
    )
    assert status == response.status_code


def test_get_ip(client):
    # tests that uploads 4 different IPs and then retrieves the information in JSON and XML format
    data = [('1.2.3.4', [1, 2], 'api-key1'),
            ('10.42.3.125', [1], 'api-key1'),
            ('23.45.2.234', [1, 2, 3], 'apikey2'),
            ('10.42.3.125', [1, 2], 'api-key1')]
    for r in data:
        response=client.post(
            '/ip_security/report_ip',
            headers={'Content-Type': 'application/json', 'api_key': r[2] },
            json={'ipAddress': r[0], 'abuseCategories': list(r[1])}
            )
        assert 201 == response.status_code

    response = client.get('/ip_security/blocked_ips/json')
    assert len(response.json)==3

    response = client.get('/ip_security/blocked_ips/xml')
    root = ET.fromstring(response.data)
    assert len(root.findall('result'))==3

    response = client.get('/ip_security/blocked_ips/json', query_string={'abuse_categories': '3'})
    assert len(response.json)==1

