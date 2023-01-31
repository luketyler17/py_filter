import sys, argparse, os, json
import yaml
import os
from yaml.loader import SafeLoader
import time
__all__ = ['get_path']

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--ifile", help="JSON file to be analyzed", required=True)
argParser.add_argument("-y", "--yaml", help="YAML Config file that contains keywords to be searched", required=True)
argParser.add_argument("-d", "--directory", help="Directory to place JSON files in, by default will use current working directory")

def main(args):
    if not args.directory:
        #make current working directory the output directory if no directory was provided
        args.directory = os.getcwd()

    with open(args.yaml) as f:
        #open yaml file for filters
        yaml_data = yaml.load(f, Loader=SafeLoader)

    with open(args.ifile) as input_file:
        #open json file and iterate through all json objects
        data = json.load(input_file)
        i = 0
        while(i < len(data)):
            x = get_path(data[i], yaml_data['filters'])
            if x:
                start_time = time.time()
                #value was found in dictionary, path and value are held within x, i is the index of the dict w/found values
                fileName = os.path.join(args.directory, x[1]+".json")
                with open(fileName, "a+") as outFile:
                    values_found = {x[0] : x[1]}
                    json.dump(values_found, outFile, indent=6)
                    json.dump(data[i], outFile, indent=6)
            i += 1




def get_path(dict_input, filter_values, prepath=""):
    __doc__ = '''Recursive function that will span all trees in json file to find specific values passed in. Takes 2 arguments to start, a dictionary input & list of values, 
                 prepath is used for the indexing of the item found. This function returns a list - x[0] is the path to the object, x[1] is the filter keyword found'''
    '''
    Function takes in three values - dictionary, the values to search for, in a list, and a prepath that is set to default to an empty string.
    Function recursively looks through dictionary for first hit of any value in the value list, when found will return a list with the path in x[0] and the value found in x[1]
    In the main() function -> this will write out the 
    '''
    if type(dict_input) is not dict:
            if type(dict_input) is dict or type(dict_input) is list:
                for index, value in enumerate(dict_input):
                    path = prepath + f"[{index}]"
                    x = get_path(value, filter_values, path)
                    if x:
                        return x
            else:
                if dict_input in filter_values:
                    path = prepath + f"[{index}]"
                    return [path, value]
                         
    else:
        for key, v in dict_input.items():
            path = prepath + f".{key}"
            if v in filter_values:
                return [path, v]
            elif type(v) is dict or type(v) is list:
                if type(v) is list:
                    #have to check if each value in list is not another nested list or dict, enumerate over the objects send lists and dicts through recursively
                    for index, value in enumerate(v):
                        new_path = path + f"[{index}]"
                        if type(value) is list:
                            #type is list, check every value to ensure no value lower is also a list/dict
                            i = 0
                            new_val = v[index]
                            while i < len(new_val):
                                third_path = new_path + f"[{i}]"
                                x = get_path(new_val[i], filter_values, third_path)
                                if x:
                                    return x
                                i += 1
                        elif type(value) is dict:
                            #have a nested dictionary, take the found dict value and submit back through get_path
                            x = get_path(value, filter_values, new_path)
                            if x:
                                return x
                        else:
                            #know type is list with no nested dicts -> search through list return the path and the item found
                            if value in filter_values:
                                return [new_path, value]
                else:
                    p = get_path(v, filter_values, path)
                    if p:
                        return p


if __name__ == "__main__":
    args = argParser.parse_args()
    main(args)