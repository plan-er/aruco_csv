import random
import time
import pandas as pd


def generate(file):
    df = pd.DataFrame([[time.time(), random.randint(0, 2), random.randint(100, 999)]])
    df.to_csv(file, mode='a', header=False, index=False)
