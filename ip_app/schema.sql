DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS blocked_ips;
DROP TABLE IF EXISTS blocked_reasons;

-- list of users registered in the system for POST methods
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  apikey TEXT NOT NULL
);

-- geo_location info of the ips
-- ip_address is not unique here since there might be more than one
CREATE TABLE ip_geo_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ipAddress TEXT,
    country TEXT,
    region TEXT,
    city TEXT,
    lat REAL,
    lng REAL,
    postalCode TEXT,
    timezone TEXT,
    domain1 TEXT,
    domain2 TEXT,
    asn INTEGER,
    name TEXT,
    route TEXT,
    domain TEXT,
    isp TEXT
);

-- list of blocked ips and the user who blocked them
CREATE TABLE blocked_ips (
  ip_id INTEGER PRIMARY KEY,
  author_id INTEGER NOT NULL,
  uploaded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ip_id) REFERENCES ip_geo_data(id),
  FOREIGN KEY (author_id) REFERENCES users(user_id)
);

-- list of reasons why an ip could be blocked
CREATE TABLE blocked_reasons(
  ip_id INTEGER PRIMARY KEY,
  PortScan BOOLEAN DEFAULT FALSE,
  Hacking BOOLEAN DEFAULT FALSE,
  SqlInjection BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (ip_id) REFERENCES blocked_ips(ip_id)
);

INSERT INTO ip_geo_data(ipAddress, country, region, city, lat, lng, postalCode, timezone, domain1, domain2, asn, name, route, domain, isp)
VALUES (
    '8.8.8.8',
    'US',
    'California',
    'Mountain View',
    37.40599,
    -122.078514,
    '94043',
    '-07:00',
    'dns1.google.com',
    'dns2.google.com',
    15169,
    'Google LLC',
    '8.8.8.0/24',
    'https://about.google/intl/en/',
    'Google LLC'
);