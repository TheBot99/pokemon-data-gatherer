import asyncio
import aiopoke
import time

MOVE_LEARN_METHOD_MAP = {
    "level-up": "level-up",
    "machine": "TM",
    "egg": "egg",
    "tutor": "tutor"
}


VERSION_NAME_TO_GENERATION = {
    'crystal': 'generation-II',
    'ruby': 'generation-III',
    'brilliant': 'generation-III',
    'gold': 'generation-II',
    'ultra': 'generation-VII',
    'lets': 'generation-VII',
    'heartgold': 'generation-IV',
    'scarlet': 'generation-IX',
    'emerald': 'generation-III',
    'sword': 'generation-VIII',
    'diamond': 'generation-IV',
    'omega': 'generation-VI',
    'platinum': 'generation-IV',
    'colosseum': 'generation-III',
    'firered': 'generation-III',
    'red': 'generation-I',
    'black': 'generation-V',
    'x': 'generation-VI',
    'yellow': 'generation-I',
    'sun': 'generation-VII',
    'xd': 'generation-III',
}

class Pokemon:
    def __init__(self, id):
        self.id = id
        self.pokemon = None
        self.species = None

    async def fetch(self):
        client = aiopoke.AiopokeClient()
        self.pokemon = await client.get_pokemon(self.id)
        self.species = await client.get_pokemon_species(self.id)

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
        generations = set(detail.version_group.name.split('-')[0] for move in self.pokemon.moves for detail in move.version_group_details)
        return list(generations)

    async def get_moves(self):
        if not self.pokemon:
            await self.fetch()
        moves_by_generation = {}
        for move in self.pokemon.moves:
            for detail in move.version_group_details:
                version_group = detail.version_group.name
                generation = VERSION_NAME_TO_GENERATION.get(version_group.split('-')[0], 'unknown')
                if generation not in moves_by_generation:
                    moves_by_generation[generation] = {"level-up": set(), "TM": set(), "egg": set(), "tutor": set()}
                if detail.move_learn_method.name == "level-up":
                    moves_by_generation[generation]["level-up"].add((move.move.name, detail.level_learned_at))
                elif detail.move_learn_method.name == "machine":
                    moves_by_generation[generation]["TM"].add(move.move.name)
                elif detail.move_learn_method.name == "egg":
                    moves_by_generation[generation]["egg"].add(move.move.name)
                elif detail.move_learn_method.name == "tutor":
                    moves_by_generation[generation]["tutor"].add(move.move.name)
        return {generation: {"level-up": list(moves["level-up"]), "TM": list(moves["TM"]), "egg": list(moves["egg"]), "tutor": list(moves["tutor"])} for generation, moves in moves_by_generation.items()}

    async def get_evolution_chain(self):
        if not self.species:
            await self.fetch()
        evolution_chain = await self.species.get_evolution_chain()
        return evolution_chain

    async def split_evolution_chain(self):
        chain = await self.get_evolution_chain()
        pre_evolution = []
        evolution = [chain.chain.species.name]
        while 'evolves_to' in chain.chain and chain.chain.evolves_to:
            chain.chain = chain.chain.evolves_to[0]
            evolution.append(chain.chain.species.name)
        pre_evolution, evolution = evolution[:-1], evolution[-1]
        return pre_evolution, evolution

    

# Use the class
async def main():
    p = Pokemon(1)  # Replace 1 with the ID of the Pokemon you want to fetch
    print(await p.get_name())
    print(await p.get_typings())
    generations = await p.get_generations()
    moves_by_generation = await p.get_moves()
    moves_by_generation_print = {}
    for generation in generations:
        moves_by_generation_print[VERSION_NAME_TO_GENERATION[generation]] = moves_by_generation.get(VERSION_NAME_TO_GENERATION[generation], [])
    #print(moves_by_generation_print)
    print(moves_by_generation.get('generation-VIII', {}))
    for generation, moves in moves_by_generation.items():
        print(f"Generation: {generation}")
        print(f"Total number of moves: {len(moves)}")
        print(f"Level-up moves: {len(moves['level-up'])}")
        print(f"TM moves: {len(moves['TM'])}")
        print(f"Egg moves: {len(moves['egg'])}")
        print(f"Tutor moves: {len(moves['tutor'])}")
        print()
    

start_time = time.time()
asyncio.run(main())
print(f"--- {time.time() - start_time} seconds ---")
