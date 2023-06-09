import re
import xml.etree.ElementTree as ET
from datetime import datetime
from http import HTTPStatus as HS
from sqlite3 import Error as SqlError
from typing import List, Dict

import requests
from flask import Blueprint, flash, g, current_app, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address  #
from validators.ip_address import ipv4
from werkzeug.exceptions import abort

from ip_app.config import Config
from ip_app.model import get_db
from ip_app.security import require_api_key

bp = Blueprint('ip_security', __name__, url_prefix='/v1/ip_security')
limiter = Limiter(key_func=get_remote_address, app=current_app)


def build_geo_ip_response(data: dict = None, query=None) -> Dict:
    """
    Formats the data from the request response into the new expected format. It uses a global id variable to count up the number of requests made to this API
    """
    assert data is not None or query is not None, "Error, either data or query must be provided"

    if data:
        if 'geo_id' not in g:
            g.geo_id = 1
        else:
            g.geo_id += 1
        return {
            'id': g.geo_id,
            'ipAddress': data["query"],
            'location': {
                'country': data["countryCode"],
                'region': data["regionName"],
                'city': data["city"],
                'lat': data["lat"],
                'lng': data["lon"],
                'postalCode': data["zip"],
                'timezone': "{:03d}:00".format(data["offset"] // 3600)
                # we convert the data to hours and write it in 24:00 format
            },
            'domains': [data["reverse"]],
            'as': {
                'asn': int(re.findall(r"\d+", data["as"])[0]),  # filter out the number
                'name': data["org"]
            },
            'isp': data["isp"]
        }
    else:
        return {
            'id': query[0],
            'ipAddress': query[1],
            'location': {
                'country': query[2],
                'region': query[3],
                'city': query[4],
                'lat': query[5],
                'lng': query[6],
                'postalCode': query[7],
                'timezone': query[8]
                # we convert the data to hours and write it in 24:00 format
            },
            'domains': [query[9], query[10]],
            'as': {
                'asn': query[11],  # filter out the number
                'name': query[12]
            },
            'isp': query[13]
        }


def insert_placeholder_geo_data(db, ip_address: str) -> int:
    """
    Inserts an IP Address in the Geo location table. For the moment, this just inserts the ip address leaving
    the rest empty. In the future it could be updated to actually fetch the data from a remote source  and insert
    it into the db
    Args:
        - db: Database object connected to the current database
        - ip_address(str): IPv4 address to be inserted
    Returns:
        the ID of the inserted value
    """
    row = db.execute('INSERT INTO ip_geo_data(ipAddress) VALUES (?) RETURNING id',
                     (ip_address,)).fetchone()

    (inserted_id,) = row if row else None
    return inserted_id


@bp.route('/ip_location/<string:ip_address>')
def get_ip_location(ip_address: str):
    """
    API that fetches the location data for a given IP address.

    Args:
        - ip_address: The IPv4 address to look up. As query parameter, it accepts the boolean external=true.
                        If true, it will fetch the data from an external provider

    Returns:
        A JSON-encoded dictionary containing the location data for the IP address.
        If the IP address is invalid a 400 Bad Request error is returned.
        If the external API fails, a 500 error is returned with a flash message describing the error.
    """



    args = request.args
    external = args.get('external', default=False, type=bool)
    # get the data from an external API provider
    if external:

        if not ipv4(ip_address):  # first, validate IP address using the validators library
            flash(f"Error, {ip_address} is not a valid ip address")
            raise ValueError(f"Error, {ip_address} is not a valid ip address")

        ip_url = Config.IP_LOCATION_API.format(ip_add=ip_address)  # add it to the default string for the request API

        try:
            response = requests.get(ip_url, timeout=7200)  # set a max timeout in case the external API fails
            response.raise_for_status()  # raise in case some HTTP Error happens

        except (ValueError, requests.exceptions.RequestException) as e:
            flash(str(e))
            abort(HS.INTERNAL_SERVER_ERROR)

        else:
            # if no errors occur during the request, transform the data and output it
            return build_geo_ip_response(response.json())

    # get the data from an internally managed DB
    else:
        try:
            if not ipv4(ip_address):  # first, validate IP address using the validators library
                flash(f"Error, {ip_address} is not a valid ip address")
                raise ValueError(f"Error, {ip_address} is not a valid ip address")
            db = get_db()
            data = db.execute('SELECT * FROM ip_geo_data WHERE ipAddress = ?',
                              (ip_address,)).fetchall()

        except SqlError as e:
            flash(f"SQL error occurred {e}")
            abort(HS.INTERNAL_SERVER_ERROR)

        else:
            res_data = build_geo_ip_response(query=data[0])
            return res_data


@bp.route('/report_ip', methods=['POST'])
@require_api_key  # decorator to require a valid registered API-key to call the method
def report_ip():
    """
    API for reporting an IP Address for malicious behaviour, uploading it to the DB. If the IP Address was already uploaded
    before, the same API can be used to update the reasons why the IP was reported
    Args:
        A JSON encoded dict is expected with the following keys:
            - ipAddress (str): the IPv4 address to be reported
            - abuseCategories (List): A list of possible categories the IP is to be reported for
            - api_key (str): A valid API key included in the headers is required to post to this method


    Returns:
        201 status code if the data was uploaded successfully
        400 error code if there are any errors with the input format
        403 error if no api-key was provided or the api-key was invalid 
    """

    try:
        # first we fetch the data
        data = request.json
        ip_address = data["ipAddress"]
        abuse_categories = data["abuseCategories"]
        api_key = request.headers.get("api_key")

        # assert the types
        if type(abuse_categories) != list:
            raise TypeError(f"Error, abuse categories must be a list, but got {type(abuse_categories)}")
        elif not set(abuse_categories).issubset({1, 2, 3}):
            raise ValueError(f"Error, only 3 types of abuse categories supported, but got {abuse_categories}")
        elif not ipv4(ip_address):
            raise ValueError(f"Error, {ip_address} is not a valid ip address")

        # now insert it into the db
        port_scan = 1 in abuse_categories
        hacking = 2 in abuse_categories
        sql_injection = 3 in abuse_categories

        # access the database
        db = get_db()
        # first we get the blocked IP
        ip_address_id = db.execute('SELECT id FROM ip_geo_data WHERE ipAddress=?',
                                   (ip_address,)).fetchall()
        if len(ip_address_id) == 0:
            ip_address_id = insert_placeholder_geo_data(db, ip_address)
        else:
            ip_address_id = ip_address_id[0][0]
        # first we insert the new registered IP in the database.
        # In case the ip has already been added we only update the time
        db.execute('INSERT INTO blocked_ips(ip_id, author_id)'
                   ' VALUES (?, (SELECT user_id FROM users WHERE apikey=?))'
                   ' ON CONFLICT(ip_id) DO UPDATE SET uploaded=?',
                   (ip_address_id, api_key, datetime.now()))
        # then we insert the reasons why it is blocked in another db.
        # In case it was already added, we just update the reasons why it was blocked
        db.execute('INSERT INTO blocked_reasons(ip_id, PortScan, Hacking, SqlInjection)'
                   ' VALUES( ?, ?, ?, ?)'
                   'ON CONFLICT(ip_id) DO UPDATE SET PortScan=?, Hacking=?, SqlInjection=?',
                   (ip_address_id, port_scan, hacking, sql_injection, port_scan, hacking, sql_injection))
        db.commit()

        return {"ipAddress": ip_address, "abuseCategories": abuse_categories}, 201

    except (KeyError, TypeError, ValueError) as e:
        flash(str(e))
        abort(HS.BAD_REQUEST)

    except SqlError as e:
        flash(f"SQL Database error {e}")
        abort(HS.INTERNAL_SERVER_ERROR)


@bp.route('/reported_ips/<string:return_format>')
@limiter.limit('10 per second', key_func=lambda: "global")  # limits the number of calls to 10/second for all users
def get_reported_ips(return_format:str):
    """
    API that fetches the blocked IPs uploaded to the DB, optionally only the abuse categories listed.

    Args:
        return_format (str): Specifies the return format to either JSON or XML

    Returns:
        A JSON or XML encoded dictionary containing the blocked IP Addresses and their reasons.
        For the JSON, the return is list filled with dictionaries with 3 keys:
            -ip_address: the string ip address
            -time_uploaed: the last time it was updated, as string datetime format
            -reasons_blocked: a list containing the reasons 1-3 for why the ip was blocked

        For the XML file, the same format and names are used
    """

    try:
        if return_format not in ["json", "xml"]:
            raise ValueError(f"Return format should be xml or json, but got {return_format}")

        db = get_db()

        # if the cateogires are passed as args, we read them and filter our query based on that
        abuse_categories = request.args.get("abuse_categories", type=str)

        if abuse_categories is not None:
            abuse_categories = [int(s) for s in abuse_categories]
            if not set(abuse_categories).issubset({1, 2, 3}):
                raise ValueError(f"Error, only 3 types of abuse categories supported, but got {abuse_categories}")

            port_scan = 1 in abuse_categories
            hacking = 2 in abuse_categories
            sql_injection = 3 in abuse_categories
            results = db.execute('SELECT g.ipAddress, p.uploaded, b.PortScan, b.Hacking, b.SqlInjection '
                                 'FROM blocked_ips p JOIN blocked_reasons b ON p.ip_id=b.ip_id JOIN ip_geo_data g '
                                 'ON g.id=b.ip_id WHERE b.PortScan=? OR b.Hacking=? OR b.SqlInjection=?',
                                 (port_scan, hacking, sql_injection)).fetchall()

        else:
            # if not, we run a query on all the parameters
            results = db.execute('SELECT g.ipAddress, p.uploaded, b.PortScan, b.Hacking, b.SqlInjection '
                                 'FROM blocked_ips p JOIN blocked_reasons b ON p.ip_id=b.ip_id JOIN ip_geo_data g '
                                 'ON g.id=b.ip_id').fetchall()


    except (ValueError, requests.exceptions.RequestException) as e:
        flash(str(e))
        abort(HS.BAD_REQUEST)

    except SqlError as e:
        flash(f"Internal DB error {e}")
        abort(HS.INTERNAL_SERVER_ERROR)

    else:
        # create the data in json format
        if return_format == 'json':
            response = []
            for query_result in results:
                reasons_blocked = []
                # build the list depending on the different non-excluyent reasons
                if query_result[2]:
                    reasons_blocked.append(1)
                if query_result[3]:
                    reasons_blocked.append(2)
                if query_result[4]:
                    reasons_blocked.append(3)

                response.append({
                    'ip_address': query_result[0],
                    'time_uploaed': query_result[1],
                    'reasons_blocked': reasons_blocked
                })

            return jsonify(response)

        # create the data in XML format
        else:
            root = ET.Element('response')
            for query_result in results:
                result = ET.SubElement(root, 'result')
                ip_address = ET.SubElement(result, 'ip_address')
                ip_address.text = str(query_result[0])
                time_uploaded = ET.SubElement(result, 'time_uploaded')
                time_uploaded.text = str(query_result[1])
                reasons_blocked = ET.SubElement(result, 'reasons_blocked')
                if query_result[2]:
                    ET.SubElement(reasons_blocked, 'reason1')
                if query_result[3]:
                    ET.SubElement(reasons_blocked, 'reason2')
                if query_result[4]:
                    ET.SubElement(reasons_blocked, 'reason3')

            return current_app.response_class(ET.tostring(root).decode('utf-8'), mimetype='application/xml')
