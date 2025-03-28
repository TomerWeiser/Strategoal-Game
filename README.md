# Strategoal

## Description
Strategoal is a two-player LAN-based strategy game developed in 2018 as a school project. Inspired by the classic board game Stratego, this game was created to demonstrate networking, game design, and programming skills. Players compete against each other by strategically moving pieces and capturing the opponent's pieces, with a leaderboard system that tracks players' performance using an SQL database.

## Project Background
* **Created in:** 2018
* **Context:** High school computer science project
* **Goal:** Develop a multiplayer network game using Python

## Features
* **Multiplayer gameplay:** Two players can connect over a LAN and compete
* **Graphical game interface:** Powered by Pygame for an interactive and engaging game experience
* **Leaderboard system:** Players can create an account, and their win/loss records are stored in the server's database
* **Strategic gameplay:** Classic Stratego-inspired piece movement and capture mechanics

## Requirements
* **Python Version:** Python 2.x
* **Required Libraries:**
   * `Pygame` (for game graphics and interaction)
   * `sqlite3` (for the leaderboard database)
   * `Tkinter` (for additional UI elements)

## Installation and Setup
1. Clone the repository from GitHub
2. Ensure you have Python 2 installed
3. Install required libraries:
   ```sh
   pip install pygame sqlite3
   ```
4. Run the server:
   ```sh
   python Server.py
   ```
5. Run the client:
   ```sh
   python Client.py
   ```
6. Ensure `Constants.py` is included in the repository before running the game

## How to Play
* Start the server and wait for a player to connect
* Each player should run `Client.py` and enter the server's IP address
* Use the Pygame interface to strategically move your pieces
* Capture opponent's pieces and aim to win the game
* The leaderboard will update automatically based on game results

## Game Mechanics
* Two players compete on a grid-based battlefield
* Each player has a set of pieces with different ranks and abilities
* Strategic placement and movement are key to victory
* Pieces can be captured based on their relative ranks

## Leaderboard
* Create a player account
* Track your wins and losses
* Compete and improve your ranking

## Note
This project was developed as a school project in 2018, showcasing early programming skills in network game development.

## Author
Tomer Weiser
