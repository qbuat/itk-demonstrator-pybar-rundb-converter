import os
import json
import ConfigParser
import numpy as np
import array
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

    def __init__(self, yarr_to_pybar=True):
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
                int_line = [int(i) for i in joined_line]
                hitbus_list.append(int_line)

        # build the pixelconfig list (list of dictionary)
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
        
        pybar_val = self._pybar_dict['CMDcnt']
        self._dict_pybar_to_json_complex['CalPulseWidth'] = 0
        self._dict_pybar_to_json_complex['CalPulseDelay'] = 0

        pybar_val = self._pybar_dict['DisableColumnCnfg']
        self._dict_pybar_to_json_complex['DisableColCnfg0'] = 0
        self._dict_pybar_to_json_complex['DisableColCnfg1'] = 0
        self._dict_pybar_to_json_complex['DisableColCnfg2'] = 0

        pybar_val = self._pybar_dict['ErrorMask']
        self._dict_pybar_to_json_complex['ErrorMask_0'] = 0
        self._dict_pybar_to_json_complex['ErrorMask_1'] = 0

        pybar_val = self._pybar_dict['SELB']
        self._dict_pybar_to_json_complex['SELB0'] = 0
        self._dict_pybar_to_json_complex['SELB1'] = 0
        self._dict_pybar_to_json_complex['SELB2'] = 0
        

    def json_to_pybar_complex_conversion(self):

        for key in complex_conversion:
            if key == 'CMDcnt':
                a = np.binary_repr(self._json_dict['CalPulseWidth'], width=16)
                b = np.binary_repr(self._json_dict['CalPulseDelay'], width=16)
                c = a[7:0:-1] + b[13:8:-1]
                self._json_keys.append(key)
                self._json_dict[key] = int(c, 2)
            if key == 'DisableColumnCnfg':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['DisableColCnfg0'] + self._json_dict['DisableColCnfg1'] + self._json_dict['DisableColCnfg2']
            if key == 'ErrorMask':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['ErrorMask_0'] + self._json_dict['ErrorMask_1']
            if key == 'SELB':
                self._json_keys.append(key)
                self._json_dict[key] =  self._json_dict['SELB0'] + self._json_dict['SELB1'] + self._json_dict['SELB2']
            if key == 'C_Inj_High':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['sCap'] + self._json_dict['lCap']

    def dump_to_pybar(self):
        from .templates import config
        out_dict = {}
        for k in common_arguments():
            print k
            out_dict[k] = self._json_dict[k]
        for p, y in pybar_yarr_matched_args():
            print p, y
            if y != 'EFUSE':
                out_dict[p] = self._json_dict[y]
            else:
                out_dict[p] = 'dummy'
                

        out_dict['CMDcnt'] = 'dummy'
        out_dict['DisableColumnCnfg'] = 'dummy'
        out_dict['ErrorMask'] = 'dummy'
        out_dict['SELB'] = 'dummy'
        out_dict['C_Inj_High'] = 'dummy'
        out_dict['Efuse_Sense'] = 'dummy'
        out_dict['GADCVref'] = 'dummy'
        out_dict['LvdsDrvSet06'] = 'dummy'
        out_dict['LvdsDrvSet12'] = 'dummy'
        out_dict['LvdsDrvSet30'] = 'dummy'
        out_dict['LvdsDrvVos'] = 'dummy'
        out_dict['TempSensDisable'] = 'dummy'
        out_dict['C_High'] = './path/path'
        out_dict['C_Low'] = './path/path'
        out_dict['Enable'] = './path/path'
        out_dict['EnableDigInj'] = './path/path'
        out_dict['FDAC'] = './path/path'
        out_dict['Imon'] = './path/path'
        out_dict['TDAC'] = './path/path'
        out_dict['Vcal_Coeff_1'] = 0.
        out_dict['Pulser_Corr_C_Inj_Low'] = None
        out_dict['Pulser_Corr_C_Inj_Med'] = None
        out_dict['Pulser_Corr_C_Inj_High'] = None

        print out_dict
        for key in sorted(out_dict.keys()):
            print key
        print len(out_dict.keys())
        print config.format(**out_dict)
        pass

    @property
    def pybar_keys(self):
        return self._pybar_keys

    @property
    def json_keys(self):
        return self._json_keys
