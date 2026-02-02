import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username = 'bob', email='bob@mail.com', password='bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str):
    # The code for task 5.1 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str, new_email:str):
    # The code for task 6 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str, email:str, password: str):
    # The code for task 7 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        newuser = User(username=username, email=email, password=password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str):
    # The code for task 8 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

# exercise 1
@cli.command()
def partial_search(search:str):
    # Exercise 1
    with get_session() as db:
        user = db.exec(select(User).where(User.username.contains(search))).first()

        if not user:
            user = db.exec(select(User).where(User.email.contains(search))).first()

        if not user:
            print("User not found")
            return
        
        print(user)

# exercise 2
@ cli.command()
def first_N_users(m: int = 0, n: int = 10):
    with get_session() as db:
        users = db.exec(select(User).offset(m).limit(n)).all()
        if not users:
            print("No users found")
            return
        
        for user in users:
            print(user)

if __name__ == "__main__":
    cli()