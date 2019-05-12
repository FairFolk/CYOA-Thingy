import xml.etree.ElementTree as ET
import random

# Tags:
QUESTION    = "question"
RANDOM      = "random"
CONSTANT    = "constant"
REPEAT      = "repeat"
EQUAL       = "equal"
GREATER     = "greater"
MACRO       = "macro"
OPTION      = "option"
FIELD       = "field"
# For equal and greater
DO          = "do"
ELSE        = "else"

# General
NAME        = "name"
VALUE       = "value"
CONFLICT    = "conflict"
OVERWRITE   = "overwrite"
ADD         = "add"
SKIP        = "skip"
APPEND      = "append"
STACK       = "stack"
CONFLICT_DEFAULT = OVERWRITE

# For questions:
SELECT      = "select"
INPUT       = "input"
YESNO       = "yesno"
YESNO_OPTS   = ["Yes", "No"]
QUESTION_DEFAULT_TYPE = SELECT

# For random:
LIST        = "list"
WEIGHT      = "weight"
RANGE       = "range"
MIN         = "min"
MAX         = "max"
RANGE_DEFAULT       = ["1", "100"]
RANDOM_DEFAULT_TYPE = LIST

# For repeat
NUMBER      = "number"
NUMBER_DEFAULT      = "2"

# For macro
SAVE        = "save"
LOAD        = "load"

# Errors:
QUESTION_MISSING    = "No question text"
INVALID_ANSWER      = "Invalid input"
VALUE_MISSING       = "No Data"

class cyoa_eval:
    def __init__(self, datapath):
        root = ET.parse(datapath).getroot()
        self.data = {}
        self.macro = {}
        self.eval_children(root)
            
    def display(self):
        print("\nResults:")
        for name, val in self.data.items():
            print(name + ": " + str(val))
    
    
    def set_data(self, node, val):
        if NAME in node.attrib:
            name = node.attrib[NAME]
            if name in self.data:
                conf = node.attrib.get(CONFLICT, CONFLICT_DEFAULT)
                if conf == OVERWRITE:
                    self.data[name] = val
                elif conf == ADD:
                    self.data[name] = int(val) + int(self.data[name])
                elif conf == APPEND:
                    self.data[name] = str(self.data[name]) + str(val)
                elif conf == STACK:
                    self.data[name] = str(self.data[name]) + "\n\t" + str(val)
                #elif conf == SKIP:
                #    pass
            else:
                self.data[name] = val

    def get_answer(self, text, opts, default=-1):
        while True:
            print(text)
            inp = input()
            if inp == "" and default > -1:
                return default
            if inp.isdigit():
                num = int(inp)
                if num > 0 and num <= len(opts):
                    return num - 1
            pos = [opt for opt in opts if opt[:len(inp)].lower() == inp.lower()]
            if len(pos) > 0:
                if len(pos) == 1:
                    return opts.index(pos[0])
                if inp.lower() in [p.lower() for p in pos]:
                    return opts.index(inp)
                
            print(INVALID_ANSWER)

    def eval_question(self, node):
        type = node.attrib.get("type", QUESTION_DEFAULT_TYPE).lower()
        ans = -1
        
        children = [child for child in node if child.tag == OPTION]
        macros = [child for child in node if child.tag == MACRO]
        for macro in macros:
            macro = self.eval_macro(macro)
            if macro != None and macro.tag == OPTION:
                children += [macro]
                    
        if type == SELECT:
            opts = [child.attrib.get(VALUE, VALUE_MISSING) for child in children]
            text = node.attrib.get("text", QUESTION_MISSING) + " (Enter Number or Substring):\n"
            text += "\n".join(str(num+1) + ") " + val for num, val in enumerate(opts))
            ans = self.get_answer(text, opts)
            
        elif type == YESNO:
            opts = YESNO_OPTS
            ans = self.get_answer(node.attrib.get("text", QUESTION_MISSING) + " ([" + opts[0] + "]/" + opts[1] + ")", opts, 0)
            
        elif type == INPUT:
            print(node.attrib.get("text", QUESTION_MISSING))
            opts = [input()]
            ans = 0
            children = []
            
        if ans < 0:
            return
            
        if NAME in node.attrib:
            self.set_data(node, opts[ans])
            
        children = list(node)
        if len(children) > ans:
            self.eval_children(children[ans])

            
    def eval_random(self, node):
        type = node.attrib.get("type", RANDOM_DEFAULT_TYPE).lower()
        choice = None
        
        if type == LIST:
            num = sum(int(child.attrib.get(WEIGHT, "1")) for child in node if child.tag == OPTION)
            sel = random.randrange(0, num)
            add = 0
            for child in node:
                add += int(child.attrib.get(WEIGHT, "1"))
                if add > sel:
                    choice = child
                    break
                    
        elif type == RANGE:
            if NAME in node.attrib:
                self.data[node.attrib[NAME]] = random.randint(int(node.attrib.get(MIN, RANGE_DEFAULT[0])), int(node.attrib.get(MAX, RANGE_DEFAULT[1])))
            return
        
        if choice == None:
            return
        
        if NAME in node.attrib:
            self.set_data(node, child.attrib.get(VALUE, VALUE_MISSING))
            
        self.eval_children(choice)
        
    def eval_equal(self, node):
        vals = [c.attrib[VALUE] for c in node.findall(CONSTANT)]
        vals += [str(self.data[f.attrib[VALUE]]) for f in node.findall(FIELD)]
        
        if len(vals) < 2 or all(v == vals[0] for v in vals[1:]):
            child = node.find(DO)
        else:
            child = node.find(ELSE)
            
        if child != None:
            self.eval_children(child)
            
    def eval_greater(self, node):
        first = None
        do = True
        for child in node:
            ct = child.tag.lower()
            if ct == CONSTANT:
                val = int(child.attrib[VALUE])
            elif ct == FIELD:
                val = int(self.data[child.attrib[VALUE]])
            else:
                continue
            
            if first == None:
                first = val
            elif first <= val:
                do = False
                break
        
        if do:
            child = node.find(DO)
        else:
            child = node.find(ELSE)
            
        if child != None:
            self.eval_children(child)
            
    def eval_macro(self, node):
        id = node.attrib.get("save", None)
        if id != None:
            self.macro[id] = node
        
        id = node.attrib.get("load", None)
        if id != None:
            return self.macro[id]
            
    def eval_children(self, node):
        for child in node:
            ct = child.tag.lower()
            
            if ct == QUESTION:
                self.eval_question(child)
                
            elif ct == RANDOM:
                self.eval_random(child)
                
            elif ct == CONSTANT:
                self.set_data(child, child.attrib.get(VALUE, VALUE_MISSING))
                
            elif ct == REPEAT:
                num = int(child.attrib.get(NUMBER, NUMBER_DEFAULT))
                for n in range(num):
                    self.eval_children(child)
                    
            elif ct == EQUAL:
                self.eval_equal(child)
                    
            elif ct == GREATER:
                self.eval_greater(child)
                
            elif ct == MACRO:
                child = self.eval_macro(child)
                if child != None:
                    self.eval_children(child)

if __name__ == "__main__":
    ev = cyoa_eval("amg.xml")
    ev.display()