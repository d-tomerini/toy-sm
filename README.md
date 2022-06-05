# Soccer manager BE light

The API service is implemented with the FASTAPI framework, according to the requirements stated in the **task_details** specifications.

## Usage
We suggest to create a python virtual environment and to install the packages listed in the `requirements.txt` file.

App can be run on a local machine using the uvicorn ASGI web server as:
- `uvicorn main:app --host 127.0.0.1 --port 8000`, where host  and port can be adapted.

## API description
FastAPI automatically provides an openAPI description at  `127.0.0.1/docs` page when the server is running.
This can also be used for testing purposes, along with other tools as `postman`.

The different routes available are:
- `/auth` for tasks related to authentication. 
  - `/auth/register` provides a form for login username and password to register a new user. If a user exist in the service it will not be allowed to register. On registration, a team is created, along with a set of players.
  -  `/auth/login` provides a JWT token to be user for authentication in user-related APIs, after providing correct username and password
- `/market` for tasks related to market activities
  - `/market/` lists all players available to be acquired. No authentication required.
  - `/market/sell` is used to sell a player. User must authenticate with a JWT, provide a `player_id` (must belong to user) and an `asking_price` parameter, that cannot be negative. Consecutive actions update the player `asking_price`.
  - `/market/withdraw` is used to remove a player on market from listing
  - `/market/buy` is used to buy a player. User must authenticate with a JWT, provide a `player_id` (must belong to another user). If the user team has enough budget, the player will be transferred to its team, budget adjusted, player value updated (based on player current value, not `asking_price`).
- `/team` for tasks related to team management. 
  - `/team/user` list the team property to the authenticated user.
  - `/team/update` provides an endpoint to update the `team_country` and the `team_name`, as parameters of the query, to the authenticated user.
- `/players` for tasks related to player management. 
  - `/players/user` list the list of players, with their current properties, to the authenticated user.
  - `/players/update` provides an endpoint to update the `player_surname`, `player_name`, `player_country`, as parameters of the query, to the authenticated user.
  
