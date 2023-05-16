# flask-ip-app
Flask app repository for the Maltego interview

The app's main functionality is to provide some security services for IP addresses. These are described in 3 APIS:

1. Geolocation API GET(/ip_security/ip_location/<string:ip_address>/) This API takes as an input parameter an string representing a valid IP Address and returns it´s worldwide location. Initially, I assumed that this API required an external request to another provided. In a real-life scenario, it would make sense to have this as information stored in an internal DB. However, due to time limitations, the app was left as an external request. 
3. Reporting API POST(/ip_security/report_ip/) This API takes as an input an IP Address and a list of possible infractions and stores it in the database. For calling this API, a secret api-key is needed. The API expects a json input with the following keys: ``` {"ipAddress":"1.2.3.4", "abuseCategories":[1, 2, 3]}```
5. Get banned IPs API GET(/ip_security/blocked_ips/<string:format>) This API returns the blocked IPs uploaded with the second API. For this API, no key is needed. The returned data is in JSON format. For an XML format, simply change json for xml in the URL. 

The project is built on top of Flask to keep the app simple to use and easy to integrate in larger code bases. All the 3 APIs are under the same Flask blueprint (ip_security) for the same reason. Further functionalities and test to be added later.

To run the project on dev mode, use
1. git clone https://github.com/A-guridi/flask-ip-app.git
2. Create a new config.py file inside the ip_app folder. In there, create a basic Config Class and a Production class.
3. conda create -n flask_app python=3.9
4. pip install -r requirments.txt 
5. flask --app ip_app init-db
6. flask --app ip_app run

This will create a DB and run the project on development mode. To run the tests, simply run pytest on the command console and you will see all the tests passed.

To deploy it as a docker, simply build and run the Dockerfile to deploy it. The deployment uses waitress as a deployment manager and install just the basic packages needed to keep it simple.

## Config classes
Config classes in the config.py file must be written in the following format:
```python
class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = ''
    FLASK_SECRET = SECRET_KEY
    DATABASE_NAME  = 'ip_app.sqlite'
    IP_LOCATION_API = 'http://ip-api.com/json/{ip_add}?fields=33619967'


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    # DB_HOST = 'my.production.database'
```
