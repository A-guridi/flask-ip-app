# flask-ip-app
Flask app repository for the Maltego interview

The app's main functionality is to provide some security services for IP addresses. These are described in 3 APIS:

1. Geolocation API GET(/ip_security/location/) This API takes as an input parameter an string representing a valid IP Address and returns it´s worldwide location.
2. Reporting API POST(/ip_security/block_ip/) This API takes as an input an IP Address and a list of possible infractions and stores it in the database. For calling this API, a secret api-key provided by me is needed. Feel free to ask me for one.
3. Get banned IPs API GET(/ip_security/blocked_ips/) This API returns the blocked IPs uploaded with the second API. For this API, no key is needed. 

The project is built on top of Flask to keep the app simple to use and easy to integrate in larger code bases. All the 3 APIs are under the same Flask blueprint (ip_security) for the same reason. Further functionalities and test to be added later.
