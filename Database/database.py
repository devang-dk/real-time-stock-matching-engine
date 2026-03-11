from sqlmodel import SQLModel, create_engine

DATABASE_URL = "postgresql://stockuser:stockpass@stock-db:5432/stockexchange"

engine = create_engine(DATABASE_URL, echo=True)