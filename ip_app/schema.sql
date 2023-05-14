DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS blocked_ips;
DROP TABLE IF EXISTS blocked_reasons;

-- list of users registered in the system for POST methods
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  apikey TEXT NOT NULL
);

-- list of blocked ips and the user who blocked them
CREATE TABLE blocked_ips (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip_address TEXT UNIQUE NOT NULL,
  author_id INTEGER NOT NULL,
  uploaded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (author_id) REFERENCES user (user_id)
);

-- list of reasons why an ip could be blocked
CREATE TABLE blocked_reasons(
  reason_id INTEGER PRIMARY KEY,
  PortScan BOOLEAN DEFAULT FALSE,
  Hacking BOOLEAN DEFAULT FALSE,
  SqlInjection BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (reason_id) REFERENCES blocked_ips (id)
);