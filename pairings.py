import random

def get_pairings():
	pass

def get_pairings_random(n):
	numbers = list(range(1, n + 1))
	random.shuffle(numbers)
	pairings = [(numbers[i], numbers[i + 1]) for i in range(0, len(numbers) - 1, 2)]
	if n % 2 != 0:
		pairings.append((numbers[-1],))
	return pairings

def get_pairings_chain():
	pass