# Pokemon Data Fetcher

This program is designed to fetch and store detailed data about Pokemon from the PokeAPI. It retrieves information such as the Pokemon's name, types, base stats, abilities, National Pokedex number, and moves. It also checks if the Pokemon has gender differences and fetches both the forms and varieties of the Pokemon.

## How to Use

1. **Setup**: First, you need to install the required libraries. You can do this by running `pip install -r requirements.txt` in your terminal.

2. **Configuration**: The program uses the Xata database to store the fetched data. You need to set your Xata API key in an environment variable named `XATA_API_KEY`.

3. **Running the program**: You can run the program by executing the main script in your terminal. For example, if the main script is named `main.py`, you can run `python main.py` in your terminal.

4. **Fetching data**: The program fetches data for a Pokemon when you call the `store_pokemon_data` function with the Pokemon's National Pokedex number as an argument. For example, `store_pokemon_data(1)` fetches data for Bulbasaur.

5. **Viewing the data**: The fetched data is stored in the `pokemon` table in your Xata database. You can view the data using the Xata dashboard.

Please note that the program uses the `aiopoke` library to fetch data from the PokeAPI, and the `xata` library to interact with the Xata database.