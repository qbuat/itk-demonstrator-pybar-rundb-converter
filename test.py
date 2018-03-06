from converter import converter

import json
from tabulate import tabulate
c = converter()
#d = c.read_from_json('dat/fei4.json')
c.read_from_pybar(
    './dat/module_0/configs/1_module_0_init_scan.cfg',
    './dat/module_0/fdacs/fdac_1_module_0_init_scan.dat',
    './dat/module_0/tdacs/tdac_1_module_0_init_scan.dat',
    [
        './dat/module_0/masks/c_high_1_module_0_init_scan.dat',
        './dat/module_0/masks/c_low_1_module_0_init_scan.dat',
        './dat/module_0/masks/c_enable_1_module_0_init_scan.dat',
        './dat/module_0/masks/imon_1_module_0_init_scan.dat',])

c.pybar_to_json_complex_conversion()
c.dump_to_json()


#d = c.read_from_json_2('dat/fei4.json')
#c.json_to_pybar_complex_conversion()



#print c.pybar_keys, len(c.pybar_keys)
#print c.json_keys, len(c.json_keys)

#intersect = list(set(c.pybar_keys) & set(c.json_keys))
#for p in sorted(intersect):
#    print p
#print 50 * '-'

#table = []
#for p in sorted(intersect):
#    table.append([p, c._json_dict[p], c._pybar_dict[p]])
#for t in pybar_yarr_mapping:

 #   p, y = t[0], t[1]
 #   if y == 'TOBEDETERMINED':
 #       table.append(['CALCULATED/{}'.format(p), c._json_dict[p], c._pybar_dict[p]])
 #   elif y == 'EFUSE':
 #       table.append(['{}/{}'.format(y, p), 'NOT AVAILABLE', c._pybar_dict[p]])
 #   else:
 #       table.append(['{}/{}'.format(y, p), c._json_dict[y], c._pybar_dict[p]])


#headers = ['key', 'YARR value', 'PYBAR value']
#print tabulate(table, headers=headers)



#only_pybar = []
#for p in c.pybar_keys:
#    if p not in intersect:
#        only_pybar.append(p)
#
#        
#only_json = []
#for p in c.json_keys:
#    if p not in intersect:
#        only_json.append(p)
#
#print only_pybar, len(only_pybar)
#
#print only_json, len(only_json)
#
#
#if len(only_pybar) < len(only_json):
#    a = ['' for i in xrange(len(only_json) - len(only_pybar))]
#    only_pybar += a
#
#if len(only_json) < len(only_pybar):
#    a = ['' for i in xrange(len(only_pybar) - len(only_json))]
#    only_json += a
#
#print len(only_pybar), len(only_json)
#
#for p, j in zip(sorted(only_pybar), sorted(only_json)):
#    print p, '\t', j
