-- passwords generated from api-key1 and apikey2

INSERT INTO users(email, apikey)
VALUES
  ('user1', 'pbkdf2:sha256:600000$8bPITmw3EzMHFttf$a8c53cbee4bbf410b1c475a7e35c907c53787ed5e904850d7e7f2a9e050522b2'),
  ('other', 'pbkdf2:sha256:600000$8oiLWha2MR9cOdIE$e8adf9a9ea759c4b61ea8f82971195b35ee2e7926d630cc2a5a9ac4bf8a6054d');

INSERT INTO blocked_ips(ip_address, author_id)
VALUES
  ('8.8.8.8', 1),
  ('10.83.42.234', 2);

INSERT INTO blocked_reasons(reason_id, PortScan, Hacking, SqlInjection)
VALUES
  (1, true, true, false),
  (2, false, false, true);