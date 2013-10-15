CREATE SCHEMA retail;
DROP TABLE IF EXISTS retail.premiums;
DROP SEQUENCE IF EXISTS retail.premium_ids_sequence;
DROP TABLE IF EXISTS retail.run_parameters;
DROP SEQUENCE IF EXISTS retail.parameter_ids_sequence;
DROP TABLE IF EXISTS retail.customer_demand;
DROP VIEW IF EXISTS retail.customer_with_market;
DROP TABLE IF EXISTS retail.customers;
DROP SEQUENCE IF EXISTS retail.customer_ids_sequence;
DROP TABLE IF EXISTS retail.markets;
DROP SEQUENCE IF EXISTS retail.market_ids_sequence;
DROP SCHEMA IF EXISTS retail;

CREATE SCHEMA retail;

CREATE SEQUENCE retail.market_ids_sequence;
CREATE TABLE retail.markets
(
  market_id INTEGER NOT NULL PRIMARY KEY DEFAULT NEXTVAL('retail.market_ids_sequence'),
  market_name CHAR(15) NOT NULL,
  country_code CHAR(2) NOT NULL,
  commodity CHAR(10) NOT NULL
);

INSERT INTO retail.markets VALUES(1, 'nbp', 'UK', 'gas');

CREATE SEQUENCE retail.customer_ids_sequence;
CREATE TABLE retail.customers
(
  customer_id integer NOT NULL PRIMARY KEY DEFAULT NEXTVAL('retail.customer_ids_sequence'),
  name CHAR(30) NOT NULL,
  market_id INTEGER NOT NULL REFERENCES retail.markets(market_id),
  image64 bytea
);

CREATE VIEW retail.customer_with_market AS
  SELECT customer_id,
         name,
         market_name,
         image64
  FROM (retail.customers
  LEFT JOIN retail.markets
  ON (retail.customers.market_id=retail.markets.market_id));

CREATE TABLE retail.customer_demand
(
  customer_id INTEGER NOT NULL REFERENCES retail.customers(customer_id),
  datetime TIMESTAMP NOT NULL,
  value FLOAT(19) NOT NULL,
  CONSTRAINT customer_demand_pkey PRIMARY KEY (customer_id, datetime)
);

CREATE SEQUENCE retail.parameter_ids_sequence;
CREATE TABLE retail.run_parameters
(
  run_id INTEGER NOT NULL PRIMARY KEY DEFAULT NEXTVAL('retail.parameter_ids_sequence'),
  market_id INTEGER NOT NULL REFERENCES retail.markets(market_id),
  parameters BYTEA NOT NULL,
  db_upload_date TIMESTAMP NOT NULL
);

INSERT INTO retail.run_parameters VALUES(1, 1, 'd', '01-Sep-13');

CREATE SEQUENCE retail.premium_ids_sequence;
CREATE TABLE retail.premiums
(
  premium_id INTEGER NOT NULL PRIMARY KEY DEFAULT NEXTVAL('retail.premium_ids_sequence'),
  run_id INTEGER NOT NULL REFERENCES retail.run_parameters(run_id),
  customer_id INTEGER NOT NULL REFERENCES retail.customers(customer_id),
  valuation_date TIMESTAMP NOT NULL,
  contract_start_date_utc TIMESTAMP NOT NULL,
  contract_end_date_utc TIMESTAMP NOT NULL,
  premium FLOAT(19) NOT NULL
);