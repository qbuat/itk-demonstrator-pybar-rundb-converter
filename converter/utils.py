import os

def convert_onefeb_onerun(converter,
                          run, 
                          module_name,
                          scan_type,
                          input_dir,
                          output_dir):

    pybar_folder = os.path.join(input_dir, module_name)
    converter.read_from_pybar(
        os.path.join(pybar_folder, '{run}_{name}_{scan}.h5'.format(run=run, name=module_name, scan=scan_type)),
        os.path.join(pybar_folder, 'configs', '{run}_{name}_{scan}.cfg'.format(run=run, name=module_name, scan=scan_type)),
        os.path.join(pybar_folder, 'fdacs', 'fdac_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),
        os.path.join(pybar_folder, 'tdacs', 'tdac_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),
        [
            os.path.join(pybar_folder, 'masks', 'c_high_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),
            os.path.join(pybar_folder, 'masks', 'c_low_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),
            os.path.join(pybar_folder, 'masks', 'enable_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),
            os.path.join(pybar_folder, 'masks', 'imon_{run}_{name}_{scan}.dat'.format(run=run, name=module_name, scan=scan_type)),])
    
    converter.pybar_to_json_complex_conversion()
    output_name = '{name}_{run}.json'.format(name=module_name, run=run)
    output = os.path.join(output_dir, output_name)
    converter.dump_to_json(output=output)


