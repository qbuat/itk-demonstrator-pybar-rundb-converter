import json
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
yarr_file = open('/Users/quentin/Downloads/jp2a.json')
pybar_file = open('/Users/quentin/software/itk-demonstrator-pybar-rundb-converter/json_out/JP2_1_255.json')


yarr_json = json.load(yarr_file)
pybar_json = json.load(pybar_file)


diffs = []
diffs_2 = []
diff_map = []

for i in xrange(len(yarr_json['FE-I4B']['PixelConfig'])):
    diff_arr = []
    print
    y_tdac = yarr_json['FE-I4B']['PixelConfig'][i]['TDAC']
    p_tdac =  pybar_json['FE-I4B']['PixelConfig'][i]['TDAC']


    for y, p in zip(y_tdac, p_tdac):
        diff_arr.append(y - p)
        diffs.append(y-p)
        p_bits = np.binary_repr(p, width=5)
        p_bits_reversed = p_bits[::-1]
        p_mod = int(p_bits_reversed, 2)
        diffs_2.append(y - p_mod)
        print y, p, p_mod, p_bits, p_bits_reversed, y-p, y-p_mod
    diff_map.append(diff_arr)

plt.figure()
plt.hist(np.array(diffs), bins=41, range=(-20.5, 20.5), label='yarr - pybar')
plt.hist(np.array(diffs_2), bins=41, range=(-20.5, 20.5), color='red', alpha=0.4, label='yarr - pybar endianness inv.')
plt.legend()


plt.figure()
plt.imshow(np.array(diff_map), interpolation='nearest', aspect='auto', cmap=plt.cm.seismic, vmin=-15, vmax=15)
plt.title('TDAC difference between yarr and pybar-converted tunings')
plt.colorbar()



keys = ['Vthin_Coarse', 'Vthin_Fine', 'TDACVbp']
value_comparison = []
for key in keys:
    vals = [
        key, 
        yarr_json['FE-I4B']['GlobalConfig'][key], 
        pybar_json['FE-I4B']['GlobalConfig'][key]
        ]
    value_comparison.append(vals)

print tabulate(value_comparison, headers=['Parameter', 'Yarr', 'pybar-converted'])
            
diff_globalconfig = []
for key in yarr_json['FE-I4B']['GlobalConfig'].keys():
    print key, yarr_json['FE-I4B']['GlobalConfig'][key], pybar_json['FE-I4B']['GlobalConfig'][key]
    diff_globalconfig.append(yarr_json['FE-I4B']['GlobalConfig'][key] - pybar_json['FE-I4B']['GlobalConfig'][key])


plt.figure()
plt.bar(
    yarr_json['FE-I4B']['GlobalConfig'].keys(),
    diff_globalconfig)



plt.show()
