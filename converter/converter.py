import os
import json
import ConfigParser
import numpy as np
import array
import shutil
import itertools
from bitarray import bitarray

from .registry import *

__all__ = [
    'converter',
]

JSON_TEMPLATE = os.path.join(os.path.dirname(__file__), '../dat/fei4.json')




class converter(object):
    """
    pybar / json converter for the ATLAS ITk 
    demonstrator
    """

    def __init__(self, yarr_to_pybar=True, run_number=1, fe_name='module_0'):
        """
        """
        self._keys = []
      #  self._json_filename
        self._pybar_keys = []
        self._json_keys  = []
        self._json_dict = {}
        self._pybar_dict = {}
        self._dict_pybar_to_json_complex = {}
        self._yarr_pixelconfig = []
        self._run_number = run_number
        self._fe_name = 'module_0'

        if yarr_to_pybar:
            print 30 * '-'
            print '--> Convert pybar files to YARR json'
            print 30 * '-'
            self.read_from_json(JSON_TEMPLATE)
        else:
            print 30 * '-'
            print '--> Convert YARR json to pybar files'
            print 30 * '-'


    def read_from_json(self, path):
        with open(path, 'r') as f:
            datastore = json.load(f)
            self._yarr_pixelconfig = datastore['FE-I4B']['PixelConfig']

            for k in datastore.keys():
                if isinstance(datastore[k], (list, dict)):
                    print k, type(datastore[k])
                else:
                    print k,type(datastore[k]), datastore[k]
                    self._json_keys.append(str(k))
                    self._json_dict[str(k)] = datastore[k]
                for kk in datastore[k].keys():
                    if isinstance(datastore[k][kk], (list, dict)):
                        print '\t', kk, type(datastore[k][kk])
                    else:
                        print '\t', kk, type(datastore[k][kk]), datastore[k][kk]
                        self._json_keys.append(str(kk))
                        self._json_dict[str(kk)] = datastore[k][kk]

                    if isinstance(datastore[k][kk], dict):
                        for kkk in datastore[k][kk].keys():
                            if isinstance(datastore[k][kk][kkk], list):
                                print '\t\t', kkk, type(datastore[k][kk][kkk])
                            else:
                                print '\t\t', kkk, type(datastore[k][kk][kkk]), datastore[k][kk][kkk]
                                self._json_keys.append(str(kkk))
                                self._json_dict[str(kkk)] = datastore[k][kk][kkk]
            return True



    def dump_to_json(self, output='tmp.json'):
        
        with open(JSON_TEMPLATE, 'r') as ftemplate:
            template_json = json.load(ftemplate)

            # hardcode new json structure
            new_json = {}
            new_json['FE-I4B'] = {
                'name': 'blurp',
                'PixelConfig': [],
                'txChannel': int(0),
                'rxChannel': int(0),
                'GlobalConfig': {},
                'Parameter': {}}


            for block in ('GlobalConfig', 'Parameter'):
                for k, val in template_json['FE-I4B'][block].iteritems():
                    arg_type = type(val)
                    # argument exist in both yarr and pybar
                    if k in common_arguments():
                        new_json['FE-I4B'][block][k] = arg_type(self._pybar_dict[k])
                    # argument needs to be computed from pybar arguments
                    if k in json_complex_conversion():
                        new_json['FE-I4B'][block][k] = self._dict_pybar_to_json_complex[k]
                    # argument exist in both yarr and pybar with different name
                    for p, y in pybar_yarr_matched_args():
                        if k == y:
                            new_json['FE-I4B'][block][k] = arg_type(self._pybar_dict[p])

            new_json['FE-I4B']['PixelConfig'] = self._yarr_pixelconfig
            new_json = json.dumps(new_json, sort_keys=True, indent=3, separators=(',', ': '))
            out_json = open(output, 'wb')
            out_json.write(new_json)


    def read_from_pybar(
        self, config, fdac, tdac, masks):
        # parse the config file
        with open(config, 'r') as config_file:
            for l in config_file.readlines():
                stripped_line = l.strip().split(' ')
                if stripped_line[0] in ('', '#'):
                    continue
                self._pybar_keys.append(stripped_line[0])
                self._pybar_dict[stripped_line[0]] = stripped_line[1]

        # parse the fdac file
        fdac_list = []
        with open(fdac, 'r') as fdac_file:
            for l in fdac_file.readlines():
                stripped_line = l.strip().replace('  ', ' ').split(' ')
                if '#' in stripped_line:
                    continue
                filtered_line = filter(lambda a: a != '', stripped_line[1:]) 
                int_filt_line = [int(i) for i in filtered_line]
                fdac_list.append(int_filt_line)

        # parse the tdac file
        tdac_list = []
        with open(tdac, 'r') as tdac_file:
            for l in tdac_file.readlines():
                stripped_line = l.strip().replace('  ', ' ').split(' ')
                if '#' in stripped_line:
                    continue
                filtered_line = filter(lambda a: a != '', stripped_line[1:]) 
                int_filt_line = [int(i) for i in filtered_line]
                tdac_list.append(int_filt_line)

        # parse the c_high, c_low and enable file
        lcap_list = []
        scap_list = []
        enable_list = []
        hitbus_list = []
        lists = [lcap_list, scap_list, enable_list]
        for l, mask in zip(lists, masks[:3]):
            print 'read', mask
            with open(mask, 'r') as file:
                for line in file.readlines():
                    if '#' in line:
                        continue
                    stripped_line = line.strip().replace('  ', '-').split('-')
                    joined_line = ''.join(stripped_line[1:])
                    int_line = [int(i) for i in joined_line]
                    l.append(int_line)

        # parse the imon file
        print 'read', masks[3]
        with open(masks[3], 'r') as file:
            for line in file.readlines():
                if '#' in line:
                    continue
                stripped_line = line.strip().replace('  ', '-').split('-')
                joined_line = ''.join(stripped_line[1:])
                int_line = [int(np.invert(np.bool(i))) for i in joined_line]
                hitbus_list.append(int_line)

        # build the pixelconfig list (list of dictionary)
        self._yarr_pixelconfig = []
        for irow, (f, t, lcap, scap, e, hitbus) in enumerate(zip(
                fdac_list, tdac_list, lcap_list, scap_list, enable_list, hitbus_list)):
            self._yarr_pixelconfig.append({
                    'Enable': e,
                    'FDAC': f, 
                    'Hitbus': hitbus,
                    'LCap': lcap,
                    'Row': irow,
                    'SCap': scap,
                    'TDAC': t})

        pass


    def pybar_to_json_complex_conversion(self):
        
        pybar_val = np.binary_repr(int(self._pybar_dict['CMDcnt']), width=14)
        self._dict_pybar_to_json_complex['CalPulseWidth'] = int(pybar_val[7::-1], 2)
        self._dict_pybar_to_json_complex['CalPulseDelay'] = int(pybar_val[13:8:-1], 2)

        pybar_val = np.binary_repr(int(self._pybar_dict['DisableColumnCnfg']), width=40)
        self._dict_pybar_to_json_complex['DisableColCnfg0'] = int(pybar_val[16::-1], 2)
        self._dict_pybar_to_json_complex['DisableColCnfg1'] = int(pybar_val[32:16:-1], 2)
        self._dict_pybar_to_json_complex['DisableColCnfg2'] = int(pybar_val[:32:-1], 2)

        pybar_val = np.binary_repr(int(self._pybar_dict['ErrorMask']), width=32)
        self._dict_pybar_to_json_complex['ErrorMask_0'] = int(pybar_val[:16], 2)
        self._dict_pybar_to_json_complex['ErrorMask_1'] = int(pybar_val[16:], 2)

        pybar_val = np.binary_repr(int(self._pybar_dict['SELB']), width=40)
        self._dict_pybar_to_json_complex['SELB0'] = int(pybar_val[16::-1], 2)
        self._dict_pybar_to_json_complex['SELB1'] = int(pybar_val[32:16:-1], 2)
        self._dict_pybar_to_json_complex['SELB2'] = int(pybar_val[:32:-1], 2)
        

    def json_to_pybar_complex_conversion(self, outdict):

        # CMDcnt
        a = bitarray(np.binary_repr(self._json_dict['CalPulseWidth'], width=8))
        b = bitarray(np.binary_repr(self._json_dict['CalPulseDelay'], width=5))
        a.reverse()
        b.reverse()
        c = a + b
        outdict['CMDcnt'] = int(c.to01(), 2)

        # DisableColumnCnfg
        a = bitarray(np.binary_repr(self._json_dict['DisableColCnfg0'], width=16))
        b = bitarray(np.binary_repr(self._json_dict['DisableColCnfg1'], width=16))
        c = bitarray(np.binary_repr(self._json_dict['DisableColCnfg2'], width=8))
        a.reverse()
        b.reverse()
        d = a + b + c
        outdict['DisableColumnCnfg'] = int(d.to01(), 2)

        # ErrorMask
        a = bitarray(np.binary_repr(self._json_dict['ErrorMask_0'], width=16))
        b = bitarray(np.binary_repr(self._json_dict['ErrorMask_1'], width=16))
        c = a + b
        outdict['ErrorMask'] = int(c.to01(), 2)

        # SELB
        a = bitarray(np.binary_repr(self._json_dict['SELB0'], width=16))
        b = bitarray(np.binary_repr(self._json_dict['SELB1'], width=16))
        c = bitarray(np.binary_repr(self._json_dict['SELB2'], width=8))
        a.reverse()
        b.reverse()
        c.reverse()
        d = a + b + c
        outdict['SELB'] = int(d.to01(), 2)

        # C_Inj_High
        a = self._json_dict['sCap']
        b = self._json_dict['lCap']
        outdict['C_Inj_High'] = a + b
        pass
        
    def dump_to_pybar(self):
        from .templates import config
        out_dict = {}

        # fill common arguments from json
        for k in common_arguments():
            out_dict[k] = self._json_dict[k]
        
        # fill arguments with different names
        for p, y in pybar_yarr_matched_args():
            print p, y
            if y != 'EFUSE':
                out_dict[p] = self._json_dict[y]
            else:
                out_dict[p] = 'dummy'
                
        # fill complex arguments that need computation
        self.json_to_pybar_complex_conversion(out_dict)

        # fill arguments pointing to auxiliary files
        out_dict['TDAC']         = 'pybar_out/tdacs/tdac_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name) 
        out_dict['FDAC']         = 'pybar_out/fdacs/fdac_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name) 
        out_dict['C_High']       = 'pybar_out/masks/c_high_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name)
        out_dict['C_Low']        = 'pybar_out/masks/c_low_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name)
        out_dict['Enable']       = 'pybar_out/masks/enable_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name)
        out_dict['EnableDigInj'] = 'pybar_out/masks/enablediginj_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name)
        out_dict['Imon']         = 'pybar_out/masks/imon_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name)


        out_dict['Pulser_Corr_C_Inj_Low'] = None
        out_dict['Pulser_Corr_C_Inj_Med'] = None
        out_dict['Pulser_Corr_C_Inj_High'] = None

        if os.path.exists('pybar_out'):
            shutil.rmtree('pybar_out')
        os.mkdir('pybar_out')
        os.mkdir('pybar_out/fdacs')
        os.mkdir('pybar_out/tdacs')
        os.mkdir('pybar_out/masks')

        config_out_name = '{0}_{1}_init_scan.cfg'.format(self._run_number, self._fe_name)
        print 'write pybar_out/%s' % config_out_name
        with open('pybar_out/{}'.format(config_out_name), 'w') as f:
            f.write(config.format(**out_dict))
        
        self.json_to_pybar_tdac_fdac('TDAC', 'pybar_out/tdacs/tdac_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('FDAC', 'pybar_out/fdacs/fdac_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('LCap', 'pybar_out/masks/c_high_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('SCap', 'pybar_out/masks/c_low_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('Enable', 'pybar_out/masks/enable_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('Enable', 'pybar_out/masks/enablediginj_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))
        self.json_to_pybar_tdac_fdac('Hitbus', 'pybar_out/masks/imon_{0}_{1}_init_scan.dat'.format(self._run_number, self._fe_name))

        pass


    def json_to_pybar_tdac_fdac(self, key, out_name):

        print 'write', out_name
        listes = []
        for d in self._yarr_pixelconfig:
            listes.append(d[key])


        with open(out_name, 'w') as f:
            intro  = '###    1  2  3  4  5  6  7  8  9 10   11 12 13 14 15 16 17 18 19 20   21 22 23 24 25 26 27 28 29 30   31 32 33 34 35 36 37 38 39 40\n'
            intro += '###   41 42 43 44 45 46 47 48 49 50   51 52 53 54 55 56 57 58 59 60   61 62 63 64 65 66 67 68 69 70   71 72 73 74 75 76 77 78 79 80\n'
            f.write(intro)
            block_line = "{0:>2} {1:>2} {2:>2} {3:>2} {4:>2} {5:>2} {6:>2} {7:>2} {8:>2} {9:>2}"
            line = """{line:>3}a  {0}   {1}   {2}   {3}\n{line:>3}b  {4}   {5}   {6}   {7}\n"""
        
            for il, l in enumerate(listes):
                blocks = [l[i * 10:(i + 1) *10] for i in xrange(8)]
                blocks_lines = [block_line.format(*b) for b in blocks]
                line_str = line.format(*blocks_lines, line=il + 1)
                f.write(line_str)
        return True

    def json_to_pybar_masks(self, key, out_name):
        print 'write', out_name
        intro = '###  1     6     11    16     21    26     31    36     41    46     51    56     61    66     71    76\n'
        block_line = '{0}{1}{2}{3}{4}-{5}{6}{7}{8}{9}'
        line = '{line:3>}  {0}  {1}  {2}  {3}  {4}  {5}  {6}  {7}\n'
        with open(out_name, 'w') as f:
            f.write(intro)
            for id, d in enumerate(self._yarr_pixelconfig):
                if key == 'Hitbus':
                    blocks = []
                    for i in xrange(8):
                        block = d[key][i * 10: (i + 1) * 10]
                        inverted_block = []
                        for bit in block:
                            invert_bit = ~bitarray(str(bit))
                            inverted_block.append(invert_bit.to01())
                        blocks.append(inverted_block)
                else:
                    blocks = [d[key][i * 10: (i + 1) * 10] for i in xrange(8)]

                blocks_lines = [block_line.format(*b) for b in blocks]
                line_str = line.format(*blocks_lines, line=id + 1)
                f.write(line_str)
    


    @property
    def pybar_keys(self):
        return self._pybar_keys

    @property
    def json_keys(self):
        return self._json_keys
