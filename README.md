# flask-ip-app
Flask app repository for the Maltego interview

The app's main functionality is to provide some security services for IP addresses. These are described in 3 APIS:

1. Geolocation API GET(/ip_security//location/ip_address/) This API takes as an input parameter an string representing a valid IP Address and returns it´s worldwide location.
2. Reporting API POST(/ip_security//report_ip/) This API takes as an input an IP Address and a list of possible infractions and stores it in the database. For calling this API, a secret api-key is needed.
3. Get banned IPs API GET(/ip_security/blocked_ips/) This API returns the blocked IPs uploaded with the second API. For this API, no key is needed. 

The project is built on top of Flask to keep the app simple to use and easy to integrate in larger code bases. All the 3 APIs are under the same Flask blueprint (ip_security) for the same reason. Further functionalities and test to be added later.

To run the project on dev mode, use
1. git clone https://github.com/A-guridi/flask-ip-app.git
2. Create a new config.py file inside the ip_app folder. In there, create a basic Config Class and a Production class.
3. conda create -n flask_app python=3.9
4. pip install -r requirments.txt 
5. flask --app ip_app init_db
6. flask --app ip_app run
This will create a DB and run the project on development mode

To deploy it as a docker, simply build and run the Dockerfile to deploy it. The deployment uses waitress as a deployment manager and install just the basic packages needed

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
