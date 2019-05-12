import xml.etree.ElementTree as ET
import random

# Tags:
QUESTION    = "question"
RANDOM      = "random"
CONSTANT    = "constant"
REPEAT      = "repeat"
EQUAL       = "equal"
GREATER     = "greater"
OPTION      = "option"

# General
NAME        = "name"
VALUE       = "value"
FIELD       = "field"
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

# For equal and greater
DO          = "do"
ELSE        = "else"

# Errors:
QUESTION_MISSING    = "No question text"
INVALID_ANSWER      = "Invalid input"
VALUE_MISSING       = "No Data"

def set_data(node, val, data):
    if NAME in node.attrib:
        name = node.attrib[NAME]
        if name in data:
            conf = node.attrib.get(CONFLICT, CONFLICT_DEFAULT)
            if conf == OVERWRITE:
                data[name] = val
            elif conf == ADD:
                data[name] = int(val) + int(data[name])
            elif conf == APPEND:
                data[name] = str(data[name]) + str(val)
            elif conf == STACK:
                data[name] = str(data[name]) + "\n\t" + str(val)
            #elif conf == SKIP:
            #    pass
        else:
            data[name] = val

def get_answer(text, opts, default=-1):
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

def eval_question(node, data):
    type = node.attrib.get("type", QUESTION_DEFAULT_TYPE).lower()
    ans = -1
    
    if type == SELECT:
        opts = [child.attrib.get(VALUE, VALUE_MISSING) for child in node if child.tag == OPTION]
        text = node.attrib.get("text", QUESTION_MISSING) + " (Enter Number or Substring):\n"
        text += "\n".join(str(num+1) + ") " + val for num, val in enumerate(opts))
        ans = get_answer(text, opts)
        
    elif type == YESNO:
        opts = YESNO_OPTS
        ans = get_answer(node.attrib.get("text", QUESTION_MISSING) + " ([" + opts[0] + "]/" + opts[1] + ")", opts, 0)
        
    elif type == INPUT:
        print(node.attrib.get("text", QUESTION_MISSING))
        opts = [input()]
        ans = 0
        
    if ans < 0:
        return
        
    if NAME in node.attrib:
        set_data(node, opts[ans], data)
        
    children = list(node)
    if len(children) > ans:
        eval_children(children[ans], data)

        
def eval_random(node, data):
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
            data[node.attrib[NAME]] = random.randint(int(node.attrib.get(MIN, RANGE_DEFAULT[0])), int(node.attrib.get(MAX, RANGE_DEFAULT[1])))
        return
    
    if choice == None:
        return
    
    if NAME in node.attrib:
        set_data(node, child.attrib.get(VALUE, VALUE_MISSING), data)
        
    eval_children(choice, data)
    
def eval_equal(node, data):
    vals = [c.attrib[VALUE] for c in node.findall(CONSTANT)]
    vals += [str(data[f.attrib[VALUE]]) for f in node.findall(FIELD)]
    
    if len(vals) < 2 or all(v == vals[0] for v in vals[1:]):
        child = node.find(DO)
    else:
        child = node.find(ELSE)
        
    if child != None:
        eval_children(child, data)
        
def eval_greater(node, data):
    first = None
    do = True
    for child in node:
        ct = child.tag.lower()
        if ct == CONSTANT:
            val = int(child.attrib[VALUE])
        elif ct == FIELD:
            val = int(data[child.attrib[VALUE]])
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
        eval_children(child, data)
        
def eval_children(node, data):
    for child in node:
        ct = child.tag.lower()
        
        if ct == QUESTION:
            eval_question(child, data)
            
        elif ct == RANDOM:
            eval_random(child, data)
            
        elif ct == CONSTANT:
            set_data(child, child.attrib.get(VALUE, VALUE_MISSING), data)
            
        elif ct == REPEAT:
            num = int(child.attrib.get(NUMBER, NUMBER_DEFAULT))
            for n in range(num):
                eval_children(child, data)
                
        elif ct == EQUAL:
            eval_equal(child, data)
                
        elif ct == GREATER:
            eval_greater(child, data)
            
def main(datapath):
    root = ET.parse(datapath).getroot()
    data = {}
    
    eval_children(root, data)
        
    print("\nResults:")
    for name, val in data.items():
        print(name + ": " + str(val))
        
    return data

if __name__ == "__main__":
    main("data.xml")