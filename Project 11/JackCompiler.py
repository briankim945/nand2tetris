import argparse
import os
import traceback

from CompilationEngine import CompilationEngine

parser = argparse.ArgumentParser(description='Convert VM code to Hack instructions.')
parser.add_argument('source', metavar='file', type=str, help='the folder to pull the jack files from')
parser.add_argument('--combine-files', help='adding flag means VMTranslator does not add the call to sys.init', action="store_true")
args = parser.parse_args()
print("args:", args)


class JackCompiler:
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

    def translate(self, combineFiles=False):
        for file in self.files:
            print(file)
            iFile = open(file)
            oFile = open(file[:-5] + ".vm", "w")
            try:
                compEngine = CompilationEngine(iFile, oFile)
                compEngine.compileClass()
            except Exception as e:
                print()
                print("Failed on " + file)
                print(e)
                print(traceback.format_exc())
            iFile.close()
            oFile.close()
        if combineFiles:
            oFile = open(self.source + "/CombinedOutput.vm", "w")
            for i, file in enumerate(self.files):
                f = file[:-5] + ".vm"
                print(f)
                iFile = open(f)
                try:
                    lines = iFile.readlines()
                    if i != 0:
                        oFile.write('\n')
                    oFile.writelines(lines)
                except Exception as e:
                    print()
                    print("Failed on " + file)
                    print(e)
                    print(traceback.format_exc())
                iFile.close()
            oFile.close()


jc = JackCompiler(args.source)
jc.translate(args.combine_files) 
