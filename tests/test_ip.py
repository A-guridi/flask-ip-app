import pytest
from ip_app.model import get_db
from flask import session
import json


@pytest.mark.parametrize(('ipAddress', 'abuseCategories', 'api_key'), (
    ('1.2.3.4', [1, 2], 'api-key1'),
    ('10.42.3.125', [1], 'api-key1'),
    ('23.45.2.234', [1, 2, 3], 'apikey2'),
))
def test_report_ip(client, ipAddress:str, abuseCategories:list, api_key:str):
    response = client.post(
        '/ip_security/report_ip',
        headers={'Content-Type': 'application/json', 'api_key': api_key },
        json={'ipAddress': ipAddress, 'abuseCategories': list(abuseCategories)}
    )
    assert 201 == response.status_code, f"Error with response {response.get_data(as_text=True)}"


@pytest.mark.parametrize(('ipAddress', 'abuseCategories', 'api_key', 'status'), (
    ('255.256.0.0', [1, 2], 'api-key1', 400),            # wrong ip add
    ('10.42.3.125', [1], 'apikey1', 403),                # wrong api-key
    ('23.45.2.234', [3, 4, 5], 'apikey2', 400),          # wrong report types
    ('23.45.2.234', [1], '', 403),                       # no api key provided
))
def test_report_ip_wrong(client, ipAddress:str, abuseCategories:list, api_key:str, status:int):
    response = client.post(
        '/ip_security/report_ip',
        headers={'Content-Type': 'application/json', 'api_key': api_key},
        json={'ipAddress': ipAddress, 'abuseCategories': list(abuseCategories)}
    )
    assert status == response.status_code
