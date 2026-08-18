from sqlmodel import Field, SQLModel


class Condition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    symptoms: str = Field(max_length=5000)
    treatment: str = Field(max_length=5000)


class Drug(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    effects: str = Field(max_length=5000)
    instructions: str = Field(max_length=5000)
