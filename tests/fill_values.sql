INSERT INTO users(email, apikey)
VALUES
  ('user1', 'api-key1'),
  ('other', 'apikey2');

-- 3 queries with random fixed data just for testing purposes
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
-- query 2
INSERT INTO ip_geo_data(ipAddress, country, region, city, lat, lng, postalCode, timezone, domain1, domain2, asn, name, route, domain, isp)
VALUES (
    '10.42.3.125',
    'UK',
    'London',
    'London City',
    51.5074,
    -0.1278,
    'SW1A 1AA',
    '+00:00',
    'dns3.google.com',
    'dns4.google.com',
    2856,
    'BT Limited',
    '10.20.30.0/24',
    'https://www.bt.com/',
    'BT Limited'
);
-- query 3
INSERT INTO ip_geo_data(ipAddress, country, region, city, lat, lng, postalCode, timezone, domain1, domain2, asn, name, route, domain, isp)
VALUES (
    '192.168.1.1',
    'Canada',
    'Ontario',
    'Toronto',
    43.6532,
    -79.3832,
    'M5V 2T6',
    '-04:00',
    'dns5.google.com',
    'dns6.google.com',
    15133,
    'Verizon Communications',
    '192.168.1.0/24',
    'https://www.verizon.com/',
    'Verizon Communications'
);