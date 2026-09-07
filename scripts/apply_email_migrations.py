"""Apply email-related migrations directly (one-off helper)."""

from sqlalchemy import text

from app.db.migrate import run_migrations
from app.db.session import SessionLocal, engine


STATEMENTS = [
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMP',
    'CREATE UNIQUE INDEX IF NOT EXISTS uq_user_email_verification_token ON "user" (email_verification_token) WHERE email_verification_token IS NOT NULL',
    'CREATE UNIQUE INDEX IF NOT EXISTS uq_user_password_reset_token ON "user" (password_reset_token) WHERE password_reset_token IS NOT NULL',
    """
    CREATE TABLE IF NOT EXISTS email_template (
        id UUID PRIMARY KEY,
        slug VARCHAR NOT NULL UNIQUE,
        name VARCHAR NOT NULL,
        description VARCHAR,
        subject VARCHAR NOT NULL,
        html_body TEXT NOT NULL,
        text_body TEXT NOT NULL,
        available_variables JSONB NOT NULL DEFAULT '[]'::jsonb,
        enabled BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS email_log (
        id UUID PRIMARY KEY,
        template_slug VARCHAR NOT NULL,
        recipient VARCHAR NOT NULL,
        subject VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        error_message TEXT,
        provider_message_id VARCHAR,
        user_id UUID REFERENCES "user"(id),
        meta JSONB,
        created_at TIMESTAMP
    )
    """,
    'UPDATE "user" SET email_verified_at = created_at WHERE email_verified_at IS NULL',
]


def main() -> None:
    with engine.begin() as conn:
        for stmt in STATEMENTS:
            conn.execute(text(stmt))
            print("applied:", stmt.strip().split("\n")[0][:100])

    run_migrations(engine)
    print("run_migrations completed")


if __name__ == "__main__":
    main()
