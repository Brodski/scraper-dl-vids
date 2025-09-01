import controllers.MicroTranscriber.transcriberGo as transcriberGo
import argparse

parser = argparse.ArgumentParser(description="Demo for argparse")

parser.add_argument("--number", type=int, default=1, help="A number input")
parser.add_argument("--query-todo", action="store_true", help="gets all the 'todos'")

args = parser.parse_args()

if __name__ == "__main__":
    print("transcriberGo gogogo!")
    transcriberGo.goTranscribeBatch(False, args)