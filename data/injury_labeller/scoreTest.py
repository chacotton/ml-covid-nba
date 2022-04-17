#TEST for injuryScore.py

import injuryScore

scoreGen = injuryScore.injuryScore("joel_embiid_2020_2021.csv", "Joel Embiid")
print(scoreGen.getInjuryScore())