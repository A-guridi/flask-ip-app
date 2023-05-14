from flask import Blueprint, flash, g, redirect, request, url_for, jsonify, make_response
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash
import requests
import re
from validators.ip_address import ipv4
from datetime import datetime

from ip_app.config import Config
from ip_app.model import get_db
from ip_app.security import require_api_key


bp = Blueprint('ip_security', __name__)


def build_geo_ip_response(data:dict):
    """
    Formats the data from the request response into the new expected format. It uses a global id variable to count up the number of requests made to this API
    """
    if 'geo_id' not in g:
        g.geo_id = 1
    else:
        g.geo_id += 1

    formatted_data={
        'id':g.geo_id,
        'ipAddress': data["query"],
        'location':{
            'country': data["countryCode"],
            'region': data["regionName"],
            'city': data["city"],
            'lat': data["lat"],
            'lng': data["lon"],
            'postalCode': data["zip"],
            'timezone': "{:03d}:00".format(data["offset"]//3600)   # we convert the data to hours and write it in 24:00 format
            },
        'domains':[data["reverse"]],
        'as':{
            'asn': int(re.findall(r"\d+", data["as"])[0]),       # filter out the number
            'name': data["org"]
            },
        'isp': data["isp"]
        }
    
    return formatted_data


@bp.route('/location/<string:ip_address>')
def get_location(ip_address):
    """
    API that fetches the location data for a given IP address.

    Args:
        ip (str): The IPv4 address to look up.

    Returns:
        A JSON-encoded dictionary containing the location data for the IP address.
        If the IP address is invalid a 400 Bad Request error is returned.
        If the external API fails, a 500 error is returned with a flash message describing the error.
    """

    if not ipv4(ip_address):            # first, validate IP address using the validators library
        flash(f"Error, {ip_address} is not a valid ip address")
        abort(400)

    ip_url = Config.IP_LOCATION_API.format(ip_add=ip_address)       # add it to the default string for the request API

    try:
        response= requests.get(ip_url, timeout=7200)        # set a max timeout in case the external API fails
        response.raise_for_status()                         # raise in case some HTTP Error happens

    except (ValueError, requests.exceptions.RequestException) as e:
        flash(str(e))
        abort(500)

    else:
        # if no errors occur during the request, transform the data and output it
        formatted_data = build_geo_ip_response(response.json())
        return formatted_data



@bp.route('/report_id', methods=['POST'])
@require_api_key                            # decorator to require a valid registered API-key to call the method
def report_ip():
    try:
        ip_address = request.form['ipAddress']
        abuse_categories = request.form['abuseCategories']
        api_key = request.headers.get("api_key")

        if type(abuse_categories) != list:
            raise TypeError(f"Abuse categories must be a list, but got {type(abuse_categories)}")
        elif not set(abuse_categories).issubset(set(1, 2, 3)):
            raise ValueError(f"Error, only 3 types of abuse categories supported, but got {abuse_categories}")
        elif not ipv4(ip_address):
            raise ValueError(f"Error, {ip_address} is not a valid ip address")

    except (KeyError, TypeError, ValueError) as e:
        flash(str(e))
        abort(400)

    else:
        # first define the reasons as bools, multiple options are allowed
        port_scan = 1 in abuse_categories
        hacking = 2 in abuse_categories
        sql_injection = 3 in abuse_categories
        # acces the database
        db = get_db()
        # first we insert the new registered IP in the database. In case the ip has already been added we only update the time
        db.execute('INSERT INTO blocked_ips(ip_address, author_id, )'
                    ' VALUES (?, SELECT user_id FROM users WHERE apikey=?)'
                    'ON CONFLICT(ip_address) DO UPDATE SET uploaded=?',
                    (ip_address, generate_password_hash(api_key), datetime.now()))
        # then we insert the reasons why its blocked in another db. In case it was already added, we just update the reasons why it was blocked
        db.execute('INSERT INTO blocked_reasons(reason_id, PortScan, Hacking, SqlInjection)'
                'VALUES (SELECT id from blocked_ips WHERE ip_address=?, ?, ?, ?)'
                'ON CONFLICT(reason_id) DO UPDATE SET PortScan=?, Hacking=?, SqlInjection=? ',
                (ip_address, port_scan, hacking, sql_injection, port_scan, hacking, sql_injection))
        db.commit()
        
        return {"ipAddress": ip_address, "abuseCategories": abuse_categories}, 201
        


