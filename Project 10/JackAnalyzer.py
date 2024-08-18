import argparse
import os
import traceback

from CompilationEngine import CompilationEngine

parser = argparse.ArgumentParser(description='Convert VM code to Hack instructions.')
parser.add_argument('source', metavar='file', type=str, help='the folder to pull the jack files from')
args = parser.parse_args()
print("args:", args)


class JackAnalyzer:
    def __init__(self, source: str):
        try:
            if len(source) > 5 and source[-5:] == ".jack":
                self.files = [source]
            else:
                self.files = [source + '/' + f for f in os.listdir(source) if len(f) > 5 and f[-5:] == ".jack"]
            print("files:", self.files)
        except Exception as e:
            print("Could not access files")
            print(e)
        self.source = source

    def translate(self):
        for file in self.files:
            print(file)
            iFile = open(file)
            oFile = file[:-5] + ".xml"
            try:
                compEngine = CompilationEngine(iFile, oFile)
                compEngine.compileClass()
                compEngine.save()
            except Exception as e:
                print()
                print("Failed on " + file)
                print(e)
                print(traceback.format_exc())
            iFile.close()
            # oFile.close()


ja = JackAnalyzer(args.source)
ja.translate() 
