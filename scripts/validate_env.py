from __future__ import annotations

from app.config import load_settings


def main() -> None:
    try:
        settings = load_settings()
    except Exception as err:  # noqa: BLE001 - surface raw error for debugging
        print(f"❌ Invalid environment: {err}")
        raise SystemExit(1) from err
    else:
        print("✅ Environment configuration looks good.")
        print(settings)


if __name__ == "__main__":
    main()
