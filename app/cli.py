import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    """
    Deletes all existing tables, recreates them and adds a user 'bob with email and password
    """
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username = 'bob', email='bob@mail.com', password='bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username: str = typer.Argument(..., help = "Username of user to retrieve")):
    """
    gets a user by username and prints it
    """
    # The code for task 5.1 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    """
    Gets all users in the database and prints them
    """

    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str = typer.Argument(..., help="Username of user whose email has to be updated"), 
                 new_email: str = typer.Argument(..., help = "New email")):
    """
    Updates the email of a user whose username is specified and prints the updated user
    """

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
def create_user(username: str = typer.Argument(..., help="Username of user to be created in database"), 
                email:str = typer.Argument(..., help="Email of user to be created in database"), 
                password: str = typer.Argument(..., help="Password of user to be created in database")):
    """
    Creates a new user in the database and prints the newly created user
    """

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
def delete_user(username: str = typer.Argument(..., help="Username of user to be deleted from database")):
    """
    Deletes a user from the database and prints a confirmation message
    """

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
def partial_search(search: str = typer.Argument(..., help="Uses a substring of username or email to search for a user")):
    """
    Searches for a user by a substring of their username or email and prints the user if found
    """

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
def first_N_users(m: int = typer.Option(0, help = "Number of users to skip from start"), 
                  n: int = typer.Option(10, help = "Number of users to retrieve")):
    """
    Retrieves and prints the first n users from the database, starting from offset m
    """

    with get_session() as db:
        users = db.exec(select(User).offset(m).limit(n)).all()
        if not users:
            print("No users found")
            return
        
        for user in users:
            print(user)

if __name__ == "__main__":
    cli()