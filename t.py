from typing import Optional, List

from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship


class HeroTeamLink(SQLModel, table=True):
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    hero_id: Optional[int] = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    headquarters: str

    heroes: List["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

    teams: List[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
    
    
    
    
sqlite_file_name = "t.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)
SQLModel.metadata.create_all(engine)
    
    
if __name__ == "__main__":
    hero1 = Hero(name="Madafaka", secret_name="Dive Wilson")
    hero2 = Hero(name='balmia', secret_name='balmia', age=20)
    team1 = Team(name="Code", headquarters="222")
    team2 = Team(name="Code2", headquarters="nai")
    
    hero1.teams.append(team1)
    hero2.teams.append(team1)
    
    
    
    with Session(engine) as db:
        # hero2 = db.exec(select(Hero).where(Hero.id == 2)).one()
        # hero2.team = None
        # db.add(hero2)
        # db.commit()
        # db.refresh(hero2)        
        # print(hero2)
        
        # hero1 = db.exec(select(Hero).where(Hero.id == 1)).one()
        # hero1.team_id = db.exec(select(Team).where(Team.id == 1)).one().id
        
        db.add(hero1)
        db.add(hero2)
        db.add(team1)
        db.add(team2)
        db.commit()
        
        db.refresh(hero1)
        db.refresh(hero2)
        db.refresh(team1)
        db.refresh(team2)
        
        
        print(hero1.dict())
        print(hero2.dict())
        print(team1.dict())
        print(team2.dict())
        
        
        
        # team1 = db.exec(select(Team).where(Team.id == 1)).one()
        # print(team1.heroes)
        pass