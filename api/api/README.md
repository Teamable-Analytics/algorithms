# Algorithm API documentation

## Requirements:
- Python 3.9+
- Docker

## Installation:
0. Contact the repository owner to get the `.env` file.
1. From the root directory of the project, run the following command:
    ```bash
    python -m pip install -r requirements.txt
    ```
2. Initialize the database by running the following command:
    ```bash
    docker-compose -f docker-compose-dev.yml up -d
    ```
3. Run migrations by running the following command:
    ```bash
    python -m manage migrate
    ```
4. Run the following command to start the API:
    ```bash
    python -m manage runserver
    ```
5. Access the API at `http://localhost:8000/`
