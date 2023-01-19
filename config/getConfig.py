# coding=utf-8
import configparser
import os
from configparser import NoSectionError, SafeConfigParser
config_file=os.getcwd()+'/config/seq2seq.ini'
if not os.path.exists(config_file):
    config_file = os.path.dirname(os.getcwd()) + '/config/seq2seq.ini'
#print(config_file)
def get_config():
    parser = SafeConfigParser()
    parser.read(config_file)
    # get the ints, floats and strings
    _conf_ints = [ (key, int(value)) for key,value in parser.items('ints')]
    _conf_floats = [ (key, float(value)) for key,value in parser.items('floats') ]
    _conf_strings = [ (key, str(value)) for key,value in parser.items('strings') ]
    _conf_train_output = [ (key, int(value)) for key,value in parser.items('train_output') ]
    return dict(_conf_ints +_conf_floats+ _conf_strings+ _conf_train_output)

def write_config(section,option,value):
    config = configparser.ConfigParser()

    try:
        config.add_section(section)
    except configparser.DuplicateSectionError:
        pass
   
    config.set(section, option, value)
    
    config.write(open(config_file, 'a+'))

def remove_config(section,option):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    try:
        config.remove_section(section)
        config.remove_option(section, option)
    except NoSectionError:
        pass
   
    config.write(open(config_file, 'w'))
