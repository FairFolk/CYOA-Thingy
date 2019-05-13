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
    Version: 0.1
'''

from cyoa_eval import *

# For field:
NAME_FORMAT = "name-format"
SEPERATOR   = "seperator"
FIELD_NAME_FORMAT_DEFAULT   = "{}: "
FIELD_SEPERATOR_DEFAULT     = "\n\t" # &#10;&#09; in XML

class cyoa_display:
    def __init__(self, disppath):
        self.root = ET.parse(disppath).getroot()
        
    def display(self, data):
        data = data.data
        for child in self.root:
            ct = child.tag.lower()
            if ct == CONSTANT:
                print(child.attrib[VALUE])
            elif ct == FIELD:
                name = child.attrib[NAME]
                val = data[name]
                if isinstance(val, list):
                    sep = child.attrib.get(SEPERATOR, FIELD_SEPERATOR_DEFAULT)
                    val = sep.join(val)
                else:
                    val = str(val)
                form = child.attrib.get(NAME_FORMAT, FIELD_NAME_FORMAT_DEFAULT)
                print(form.format(name) + val)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display data evaluated with cyao_eval.py')
    parser.add_argument('data_path', help= 'Path to the XML file to be evaluated')
    parser.add_argument('disp_path', help= 'Path to the XML file describing the display format')
    args = parser.parse_args()
    disp = cyoa_display(args.disp_path)
    
    data = cyoa_eval(args.data_path)
    disp.display(data)
    