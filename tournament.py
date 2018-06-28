# Tournament Database (Swiss Pairing)
# Developed by: Alfred Vivek
# Version: 1.0

# Run the python code just by changing the database connection parameters below.
# It automatically creates a database and the schema and runs the tournament.

import math
import psycopg2
from random import *
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# This function takes two inputs and inserts the player name into the records
#Input 1 : Name
#Input 2 : Connection Object
def registerPlayer(name,conn):
	cursor=conn.cursor()
	cursor.execute("INSERT INTO PLAYERS VALUES (DEFAULT,%s,0,0);",(name,))
	conn.commit()

# This function takes one input and returns count of players from the records
#Input : Connection Object
#Output : Count of players in the tournament
def countPlayers(conn):
	cursor=conn.cursor()
	cursor.execute("select count(*) from PLAYERS")
	result=cursor.fetchall();
	return result[0][0]

# This function takes one input and deletes all the records from the players table
#Input : Connection Object
#Output : Deletes all the records from the players table
def deletePlayers(conn):
	cursor=conn.cursor()
	cursor.execute("TRUNCATE PLAYERS RESTART IDENTITY")
	conn.commit()

# This function takes three inputs and inserts match results as well as updates the players table
#Input 1: Winner
#Input 2: Loser
#Input 3: Connection Object
#Output : Inserts match results as well as updates the players table
def reportMatch(winner,loser,conn):
	cursor=conn.cursor()
	cursor.execute("INSERT INTO MATCHES VALUES (DEFAULT,%s,%s);",(winner,loser))
	cursor.execute("SELECT WINS FROM PLAYERS WHERE PLAYER_ID='%s'"%(winner))
	result=cursor.fetchall();
	result=result[0][0]
	cursor.execute("UPDATE PLAYERS SET WINS=%d WHERE PLAYER_ID=%d"%(result+1,winner))
	cursor.execute("SELECT LOSS FROM PLAYERS WHERE PLAYER_ID='%s'"%(loser))
	result=cursor.fetchall();
	result=result[0][0]
	cursor.execute("UPDATE PLAYERS SET LOSS=%d WHERE PLAYER_ID=%d"%(result+1,loser))
	conn.commit()

# This function takes one input and displays the match result
#Input 1: Connection Object
#Output : Displays the match result
def matchResult(conn):
	cursor = conn.cursor()
	cursor.execute("SELECT *,PLAYER_NAME FROM MATCHES,PLAYERS WHERE MATCHES.WINNER=PLAYERS.PLAYER_ID")
	result = cursor.fetchall();
	print("----------Match Results----------")
	for r in result:
		print("Match %s>   %s  Vs  %s Winner : %s\n"%(r[0],r[1],r[2],r[4]))

# This function takes one input and deletes all the records from the matches table
#Input : Connection Object
#Output : Deletes all the records from the matches table
def deleteMatches(conn):
	cursor=conn.cursor()
	cursor.execute("TRUNCATE MATCHES RESTART IDENTITY")
	conn.commit()

# This function takes one input and displays the player standings after the current round
#Input : Connection Object
#Output : Displays the player standings after the current round
def playerStandings(conn):
	cursor=conn.cursor()
	cursor.execute("SELECT PLAYER_ID,PLAYER_NAME,WINS FROM PLAYERS ORDER BY WINS DESC")
	result=cursor.fetchall();
	i=1
	for r in result:
		print(i,r)
		i=i+1

# This function takes one input and computes the swiss pairings
#Input : Connection Object
#Output : Computes the Swiss Pairings
def swissPairings(n,conn):
	cursor = conn.cursor()
	cursor.execute("SELECT PLAYER_NAME FROM PLAYERS ORDER BY WINS DESC")
	result=cursor.fetchall();
	for i in range(0,n-1,2):
		player1 = result[i][0]
		player2 = result[i+1][0]
		print("%s  VS  %s\n"%(player1,player2))

# This function takes three inputs and computes the main game
#Input 1 : Number of Players
#Input 2 : Round Number
#Input 3 : Connection Object
def playTournament(n,x,conn):	
	print("Total players in the tournament : ",countPlayers(conn))
	print("----------------ROUND %s----------------"%(x+1))
	swissPairings(n,conn)
	cursor = conn.cursor()
	cursor.execute("SELECT PLAYER_ID FROM PLAYERS ORDER BY WINS DESC")
	result=cursor.fetchall();	
	for i in range(0,n-1,2):
		player1 = result[i][0]
		player2 = result[i+1][0]
		if(randint(1,2)==1):
			reportMatch(player1,player2,conn)
		else:
			reportMatch(player2,player1,conn)
	matchResult(conn)
	print("----------Player Standings----------")
	playerStandings(conn)

#Driver Function that takes inserts the players into the table and starts the tournament
conn = psycopg2.connect("user='postgres' host='localhost' password='vivek123'")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor();
print("Creating Database..........")
cursor.execute("CREATE DATABASE TOURNAMENT;")
conn = psycopg2.connect("dbname='tournament' user='postgres' password='vivek123'")
cursor = conn.cursor();
cursor.execute("CREATE TABLE PLAYERS(player_id serial not null,player_name varchar(100) not null,wins int not null,loss int not null);")
cursor.execute("CREATE TABLE MATCHES(match_id serial not null,winner int not null,loser int not null);") 
n = int(input("Enter the number of Players!!"))
deletePlayers(conn)
for i in range (0,n):
	name = input("Enter Name : %d "%(i+1))
	registerPlayer(name,conn)
for x in range (0,int(math.log(n,2))):
	deleteMatches(conn)
	playTournament(n,x,conn)
cursor.execute("SELECT PLAYER_NAME FROM PLAYERS ORDER BY WINS DESC")
result=cursor.fetchall();
print("Winner is : %s"%(result[0]))
conn.close()