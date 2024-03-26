import asyncio
import aiopoke
import time
import json
import os
from xata.client import XataClient

xata = XataClient(
    api_key=os.environ.get("XATA_API_KEY"), db_url=os.environ.get("XATA_DB_URL")
)

MOVE_LEARN_METHOD_MAP = {
    "level-up": "level-up",
    "machine": "TM",
    "egg": "egg",
    "tutor": "tutor",
}


VERSION_NAME_TO_GENERATION = {
    "crystal": "generation-II",
    "ruby": "generation-III",
    "brilliant": "generation-III",
    "gold": "generation-II",
    "ultra": "generation-VII",
    "lets": "generation-VII",
    "heartgold": "generation-IV",
    "scarlet": "generation-IX",
    "emerald": "generation-III",
    "sword": "generation-VIII",
    "diamond": "generation-IV",
    "omega": "generation-VI",
    "platinum": "generation-IV",
    "colosseum": "generation-III",
    "firered": "generation-III",
    "red": "generation-I",
    "black": "generation-V",
    "x": "generation-VI",
    "yellow": "generation-I",
    "sun": "generation-VII",
    "xd": "generation-III",
}


class Pokemon:
    def __init__(self, id):
        self.id = id
        self.pokemon = None
        self.species = None

    async def fetch(self):
        client = aiopoke.AiopokeClient()
        self.pokemon = await client.get_pokemon(self.id)
        

    async def get_name(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.name

    async def get_typings(self):
        if not self.pokemon:
            await self.fetch()
        return [type.type.name for type in self.pokemon.types]

    async def get_generations(self):
        if not self.pokemon:
            await self.fetch()
        generations = set(
            detail.version_group.name.split("-")[0]
            for move in self.pokemon.moves
            for detail in move.version_group_details
        )
        return list(generations)

    async def get_moves(self):
        if not self.pokemon:
            await self.fetch()
        moves_by_generation = {}
        for move in self.pokemon.moves:
            for detail in move.version_group_details:
                version_group = detail.version_group.name
                generation = VERSION_NAME_TO_GENERATION.get(
                    version_group.split("-")[0], "unknown"
                )
                if generation not in moves_by_generation:
                    moves_by_generation[generation] = {
                        "level-up": set(),
                        "TM": set(),
                        "egg": set(),
                        "tutor": set(),
                    }
                if detail.move_learn_method.name == "level-up":
                    moves_by_generation[generation]["level-up"].add(
                        (move.move.name, detail.level_learned_at)
                    )
                elif detail.move_learn_method.name == "machine":
                    moves_by_generation[generation]["TM"].add(move.move.name)
                elif detail.move_learn_method.name == "egg":
                    moves_by_generation[generation]["egg"].add(move.move.name)
                elif detail.move_learn_method.name == "tutor":
                    moves_by_generation[generation]["tutor"].add(move.move.name)
        return {
            generation: {
                "level-up": list(moves["level-up"]),
                "TM": list(moves["TM"]),
                "egg": list(moves["egg"]),
                "tutor": list(moves["tutor"]),
            }
            for generation, moves in moves_by_generation.items()
        }

    async def get_abilities(self):
        if not self.pokemon:
            await self.fetch()
        hidden_abilities = ""
        non_hidden_abilities = []
        for ability in self.pokemon.abilities:
            ability_name = ability.ability.name
            is_hidden = ability.is_hidden
            if is_hidden:
                hidden_abilities = ability_name
            else:
                non_hidden_abilities.append(ability_name)
        return hidden_abilities, non_hidden_abilities

    async def get_base_stats(self):
        if not self.pokemon:
            await self.fetch()
        base_stats = {}
        for stat in self.pokemon.stats:
            base_stats[stat.stat.name] = stat.base_stat
        return base_stats

    async def get_weight(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.weight

    async def get_height(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.height

    async def get_front_sprite_default(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.sprites.front_default.url

    async def get_front_sprite_shiny(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.sprites.front_shiny.url

    async def get_front_female_sprite_default(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.sprites.front_female.url

    async def get_front_female_sprite_shiny(self):
        if not self.pokemon:
            await self.fetch()
        return self.pokemon.sprites.front_shiny.url


async def main():
    records = xata.data().query("pokemon", {
  "page": {
    "size": 1000 # limit result set to 25 records
  }
})
    #print(records)
    records = records["records"]
    for record in records:
        if record["varieties"] != []:
            print(record["name"], record["varieties"])
            for variety in record["varieties"]:
                p = Pokemon(variety)
                await p.fetch()

                print(await p.get_name())

                moves_by_generation = await p.get_moves()

                # Convert the moves dictionary to a JSON string
                moves_json = json.dumps(moves_by_generation, indent=3)
                generations = await p.get_generations()
                generations_list = []
                for generation in generations:
                    generations_list.append(VERSION_NAME_TO_GENERATION.get(generation, "unknown"))
                    generations_list = list(set(generations_list))

                
                front_female_sprite_default = None
                front_female_sprite_shiny = None

                try:
                    front_sprite_default = await p.get_front_sprite_default()
                except:
                    front_sprite_default = None

                try:
                    front_sprite_shiny = await p.get_front_sprite_shiny()
                except:
                    front_sprite_shiny = None

                data = xata.records().insert("varieties", {
                    "name": await p.get_name(),
            "types": await p.get_typings(),
            "hp": (await p.get_base_stats())["hp"],
            "attack": (await p.get_base_stats())["attack"],
            "defense": (await p.get_base_stats())["defense"],
            "special-attack": (await p.get_base_stats())["special-attack"],
            "special-defense": (await p.get_base_stats())["special-defense"],
            "speed": (await p.get_base_stats())["speed"],
            "hidden-ability": (await p.get_abilities())[0],
            "abilities": (await p.get_abilities())[1],
            "moves": moves_json,
            "generations": generations_list,
            "default-pokemon": record["name"],
            "weight": await p.get_weight(),
            "height": await p.get_height(),
            "front_sprite_default": front_sprite_default,
            "front_sprite_shiny": front_sprite_shiny,
            "front_female_sprite_default": front_female_sprite_default,
            "front_female_sprite_shiny": front_female_sprite_shiny
                })
                print(data)
                
                
        
asyncio.run(main())