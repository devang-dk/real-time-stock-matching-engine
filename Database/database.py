from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://stockuser:stockpass@stock-db:5432/stockexchange"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session