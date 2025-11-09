from src.database import SessionLocal
from src.models import APIIntegration

if __name__ == "__main__":
    s = SessionLocal()
    try:
        if not s.query(APIIntegration).count():
            s.add_all([
                APIIntegration(name='google_books', display_name='Google Books', priority=1, is_enabled=True),
                APIIntegration(name='open_library', display_name='Open Library', priority=2, is_enabled=True),
            ])
            s.commit()
            print('Seeded integrations')
        else:
            print('Integrations already present')
    finally:
        s.close()
