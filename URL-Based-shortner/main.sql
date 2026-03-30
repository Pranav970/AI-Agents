CREATE TABLE url_mappings (
  id SERIAL PRIMARY KEY,
  short_code VARCHAR(10) NOT NULL UNIQUE,
  original_url TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP
);
CREATE INDEX ON url_mappings (created_at);
CREATE TABLE click_events (
  id SERIAL PRIMARY KEY,
  short_code VARCHAR(10) NOT NULL,
  clicked_at TIMESTAMP NOT NULL DEFAULT NOW(),
  referrer TEXT,
  user_agent TEXT
);
