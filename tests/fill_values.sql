-- passwords generated from api-key1 and apikey2

INSERT INTO users(email, apikey)
VALUES
  ('user1', 'api-key1'),
  ('other', 'apikey2');

INSERT INTO blocked_ips(ip_address, author_id)
VALUES
  ('8.8.8.8', 1),
  ('10.83.42.234', 2);

INSERT INTO blocked_reasons(reason_id, PortScan, Hacking, SqlInjection)
VALUES
  (1, true, true, false),
  (2, false, false, true);