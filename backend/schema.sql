CREATE TABLE IF NOT EXISTS meetings (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL DEFAULT 'Untitled',
  status TEXT NOT NULL DEFAULT 'queued',
  transcript TEXT,
  attendees TEXT[] NOT NULL DEFAULT '{}',
  meeting_date DATE NOT NULL DEFAULT CURRENT_DATE,
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS action_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
  task TEXT NOT NULL,
  owner TEXT,
  due_date DATE,
  due_text TEXT,
  evidence_quote TEXT,
  confidence TEXT,
  flagged BOOLEAN NOT NULL DEFAULT FALSE,
  decision TEXT NOT NULL DEFAULT 'pending',
  external_id TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  meeting_id UUID,
  action TEXT NOT NULL,
  detail JSONB,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);
