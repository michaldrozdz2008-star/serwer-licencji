import os
from contextlib import contextmanager

import psycopg


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError("Brak DATABASE_URL w zmiennych środowiskowych")


@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_license(license_key: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select license_key, status, hwid_hash, expires_at
                from licenses
                where license_key = %s
                """,
                (license_key,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "license_key": row[0],
                "status": row[1],
                "hwid_hash": row[2],
                "expires_at": row[3],
            }


def activate_license(license_key: str, hwid_hash: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select status, hwid_hash, expires_at
                from licenses
                where license_key = %s
                """,
                (license_key,),
            )
            row = cur.fetchone()

            if not row:
                return {"status": "invalid", "message": "License not found"}

            status, saved_hwid, expires_at = row

            if status == "banned":
                return {"status": "banned", "message": "License banned"}

            if status == "expired":
                return {"status": "expired", "message": "License expired"}

            if expires_at is not None:
                cur.execute("select now() > %s", (expires_at,))
                if cur.fetchone()[0]:
                    return {"status": "expired", "message": "License expired"}

            if saved_hwid is None:
                cur.execute(
                    """
                    update licenses
                    set hwid_hash = %s,
                        status = 'active',
                        activated_at = now(),
                        last_seen = now()
                    where license_key = %s
                    """,
                    (hwid_hash, license_key),
                )
                cur.execute(
                    """
                    insert into activations (license_key, hwid_hash, event_type)
                    values (%s, %s, 'activate')
                    """,
                    (license_key, hwid_hash),
                )
                conn.commit()
                return {"status": "valid", "message": "License activated"}

            if saved_hwid != hwid_hash:
                cur.execute(
                    """
                    insert into activations (license_key, hwid_hash, event_type)
                    values (%s, %s, 'hwid_mismatch')
                    """,
                    (license_key, hwid_hash),
                )
                conn.commit()
                return {"status": "hwid_mismatch", "message": "License used on another device"}

            cur.execute(
                """
                update licenses
                set last_seen = now()
                where license_key = %s
                """,
                (license_key,),
            )
            cur.execute(
                """
                insert into activations (license_key, hwid_hash, event_type)
                values (%s, %s, 'validate')
                """,
                (license_key, hwid_hash),
            )
            conn.commit()
            return {"status": "valid", "message": "License valid"}


def create_license(license_key: str, notes: str = ""):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into licenses (license_key, status, notes)
                values (%s, 'unused', %s)
                on conflict (license_key) do nothing
                """,
                (license_key, notes),
            )
            conn.commit()
