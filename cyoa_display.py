'''
    cyoa_display.py: Displays data evaluated with cyao_eval.py
    Usage: python ./cyoa_display.py [-h] data_path disp_path
    Arguments:
        data_path: Path to the XML file to be evaluated
        disp_path: Path to the XML file describing the display format
        -h:   Display usage information
    Python version: 3.7.3
    
    Author:  Unseelie
    Email:   unseelie@gmx.at
    Version: 0
'''

from cyoa_eval import *

class cyoa_display:
    def __init__(self, path):
        pass
        
    def display(self, data):
        data = data.data
        print(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display data evaluated with cyao_eval.py')
    parser.add_argument('data_path', help= 'Path to the XML file to be evaluated')
    parser.add_argument('disp_path', help= 'Path to the XML file describing the display format')
    args = parser.parse_args()
    data = cyoa_eval(args.data_path)
    disp = cyoa_display(args.disp_path)
    disp.display(data)
    