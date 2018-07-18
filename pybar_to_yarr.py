from converter import converter, pybar_run, ALL_FEBS
from converter.utils import convert_onefeb_onerun

if __name__ == '__main__':

    pybar_runs = [
        pybar_run(255, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(256, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(260, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        pybar_run(261, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(262, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(263, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        pybar_run(264, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(265, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(266, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        pybar_run(268, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(269, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(270, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        pybar_run(271, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(272, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(273, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        pybar_run(274, run_type='analog_scan', febs=ALL_FEBS),
        pybar_run(275, run_type='threshold_scan', febs=ALL_FEBS),
        pybar_run(277, run_type='noise_occupancy_tuning', febs=ALL_FEBS),
        ]

    converter = converter(pybar_to_yarr=True)
    input_dir = '/Volumes/01/FullStaveRun_2A_CoolantM15/'
    output_dir = './json_out'

    for pb_run in pybar_runs:
        for feb in pb_run.febs:
            print
            convert_onefeb_onerun(converter, 
                                  pb_run.run_number,
                                  feb,
                                  pb_run.run_type,
                                  input_dir,
                                  output_dir)


    
