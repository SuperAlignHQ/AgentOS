### Steps to setup backend server

* Make sure uv is installed on your system - https://github.com/astral-sh/uv
* Clone the repository
* Run `uv sync` to install dependencies
* Make sure you are in `Classification Backend` directory
* Run `uvicorn main:app --port 8079` to start the server
* The server will start on `http://localhost:8079`
* You can access the API documentation on `http://localhost:8079/docs`