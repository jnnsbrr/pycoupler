import os
import subprocess
import json


class SubConfig:
    """This serves as an LPJmL config class that can be easily accessed,
    converted to a dictionary or written as a json file. It also provides
    methods to get/set outputs, restarts and sockets for model coupling.

    :param config_dict: takes a dictionary (ideally LPJmL config dictionary)
        and builds up a nested LpjmLConfig class with corresponding fields
    :type config_dict: dict
    """
    def __init__(self, config_dict):
        """Constructor method
        """
        self.__dict__.update(config_dict)

    def to_dict(self):
        """Convert class object to dictionary
        """
        def obj_to_dict(obj):
            if not hasattr(obj, '__dict__'):
                return obj
            result = {}
            for key, val in obj.__dict__.items():
                if key.startswith("_"):
                    continue
                element = []
                if isinstance(val, list):
                    for item in val:
                        element.append(obj_to_dict(item))
                else:
                    element = obj_to_dict(val)
                result[key] = element
            return result
        return obj_to_dict(self)

    def to_json(self, path):
        """Write json file
        :param file: file name (including relative/absolute path) to write json
            to
        :type: str
        """
        # convert class to dict
        config_dict = self.to_dict()

        # configuration file name
        json_file = f"{path}/config_{self.sim_name}.json"

        # write json and prettify via indent
        with open(json_file, 'w') as con:
            json.dump(config_dict, con, indent=2)

        return json_file

    def __repr__(self):
        return f"<{self.__class__.__name__} object>"


class LpjmlConfig(SubConfig):

    def fields(self):
        """Return object fields
        """
        return list(self.__dict__.keys())

    def get_inputs(self, id_only=True, inputs=None):
        """
        Get defined inputs as list
        """
        if id_only:
            if inputs:
                return [
                    key for key in self.input.__dict__.keys() if key in inputs]
            else:
                return list(self.input.__dict__.keys())
        else:
            if inputs:
                return {key: self.input.to_dict()[key] for key in inputs}
            else:
                return self.input.to_dict()

    def get_outputs_avail(self, id_only=True, with_description=True):
        """Get available output (outputvar) names (== output ids) as list
        """
        if id_only:
            if with_description:
                return {out.name: out.descr for out in self.outputvar}
            else:
                return [out.name for out in self.outputvar]
        else:
            return self.to_dict()["outputvar"]

    def get_outputs(self, id_only=True):
        """Get defined output ids as list
        """
        if id_only:
            return [out.id for out in self.output]
        else:
            return self.to_dict()['output']

    def set_spinup(self, sim_path):
        """Set configuration required for spinup model runs
        :param sim_path: define sim_path data is written to
        :type sim_path: str
        :param restart_path: define restart_path the restart files to start
            model runs from. Has to match with `restart_path` from
            `set_historic`
        :type restart_path: str
        """
        self.sim_name = "spinup"
        output_path = f"{sim_path}/output/{self.sim_name}"

        # set output writing
        self.set_output_path(output_path)
        # set restart directory to restart from in subsequent historic run
        self.set_restart(path=sim_path)

        return output_path

    def set_historic(self, sim_path, start_year, end_year,
                     write_start_year=None, write_outputs=[],
                     write_temporal_resolution=None,
                     append_output=True):
        """Set configuration required for historic model runs
        :param sim_path: define sim_path data is written to
        :type sim_path: str
        :param start_year: start year of simulation
        :type start_year: int
        :param end_year: end year of simulation
        :type end_year: int
        :param write_start_year: first year of output being written
        :type write_start_year: int
        :param write_outputs: output ids of `outputs` to be written by
            LPJmL. Make sure to check if required output is available via
            `get_outputs_avail`
        :type write_outputs: list
        :param write_temporal_resolution: list of temporal resolutions
            corresponding to `outputs` or str to set the same resolution for
            all `outputs`. Choose between "annual", "monthly", "daily".
            Defaults to None (use default output/outputvar resolution).
        :type write_temporal_resolution: list/str/None
        :param append_output: if True defined output entries are appended by
            defined `outputs`. Please mind that the existing ones are not
            altered.
        :param append_output: bool
        """
        self.sim_name = "historic"
        output_path = f"{sim_path}/output/{self.sim_name}"
        # set time range for historic run
        self.set_timerange(start_year=start_year,
                           end_year=end_year,
                           write_start_year=write_start_year)
        # set output writing
        self.set_outputs(output_path,
                         outputs=write_outputs,
                         temporal_resolution=write_temporal_resolution,
                         file_format="cdf",
                         append_output=append_output)
        # set start from directory to start from spinup run
        self.set_startfrom(path=sim_path)
        # set restart directory to restart from in subsequent transient run
        self.set_restart(path=sim_path)

        return output_path

    def set_coupled(self, sim_path, start_year, end_year,
                    couple_inputs, couple_outputs,
                    write_outputs=[],
                    write_temporal_resolution=None,
                    append_output=True,
                    model_name="copan:CORE"):
        """Set configuration required for coupled model runs
        :param sim_path: define sim_path data is written to
        :type sim_path: str
        :param start_year: start year of simulation
        :type start_year int
        :param end_year: end year of simulation
        :type end_year: int
        :param couple_inputs: list of inputs to be used as socket for coupling.
            Provide dictionary/json key as identifier -> entry in list.
        :type couple_inputs: list
        :param couple_outputs: list of outputs to be used as socket for
            coupling. Provide output id as identifier -> entry in list.
        :type couple_outputs: list
        :param write_outputs: output ids of `outputs` to be written by
            LPJmL. Make sure to check if required output is available via
            `get_outputs_avail`
        :type write_outputs: list
        :param write_temporal_resolution: list of temporal resolutions
            corresponding to `outputs` or str to set the same resolution for
            all `outputs`. Choose between "annual", "monthly", "daily".
            Defaults to None (use default output/outputvar resolution).
        :type write_temporal_resolution: list/str/None
        :param append_output: if True defined output entries are appended by
            defined `outputs`. Please mind that the existing ones are not
            altered.
        :param append_output: bool
        :param model_name: model name of the coupled program which also sets
            the model to coupled mode (without coupling coupled_model = None)
        :type model_name: str
        """
        self.sim_name = "coupled"
        output_path = f"{sim_path}/output/{self.sim_name}"
        # set time range for coupled run
        self.set_timerange(start_year=start_year, end_year=end_year)
        # set output directory, outputs (relevant ones for pbs and agriculture)
        write_outputs += [
            item for item in couple_outputs if item not in write_outputs
        ]
        self.set_outputs(output_path,
                         outputs=write_outputs,
                         temporal_resolution=write_temporal_resolution,
                         file_format="cdf",
                         append_output=append_output)
        # set coupling parameters
        self.set_coupler(inputs=couple_inputs, outputs=couple_outputs,
                         model_name=model_name)
        # set start from directory to start from historic run
        self.set_startfrom(path=sim_path)

        return output_path

    def set_outputs(self, output_path, outputs=[], file_format="raw",
                    temporal_resolution="annual", append_output=True):
        """Set outputs to be written by LPJmL, define temporal resolution
        :param output_path: define output_path the output is written to. If
            `append_output == True` output_path is only altered for appended
            `outputs`.
        :type output_path: str
        :param outputs: output ids of `outputs` to be written by LPJmL. Make
            sure to check if required output is available via
            `get_outputs_avail`
        :type outputs: list
        :param file_format: file format for `outputs` (not to be used for
            sockets!). "raw" (binary), "clm" (binary with header) and "cdf"
            (NetCDF) are availble. Defaults to "raw".
        :type file_format: str
        :param temporal_resolution: list of temporal resolutions corresponding
            to `outputs` or str to set the same resolution for all `outputs`.
            Defaults to "annual" (for all `outputs`).
        :type temporal_resolution: list/str
        :param append_output: if True defined output entries are appended by
            defined `outputs`. Please mind that the existing ones are not
            altered.
        :param append_output: bool
        """
        available_res = ('annual', 'monthly', 'daily')
        available_formats = {'raw': 'bin', 'clm': 'clm', 'cdf': 'nc4'}
        nonvariable_outputs = ('globalflux')

        # add grid output if not already defined
        if "grid" not in outputs:
            outputs.append("grid")
            if isinstance(temporal_resolution, list) > 1:
                temporal_resolution.append("annual")

        if temporal_resolution:
            # check if temporal resolution is of length one
            if isinstance(temporal_resolution, list):
                temp_res = temporal_resolution
                if len(outputs) != len(temporal_resolution):
                    raise ValueError("outputs and temporal_resolution have a" +
                                     " different length. Please adjust.")
            else:
                temp_res = [temporal_resolution]

            # check if temporal resolution is available
            if any(res not in available_res for res in temp_res):
                raise ValueError("Temporal resolution not available for " +
                                 "LPJmL. Choose from 'annual', 'monthly' " +
                                 "and 'daily'.")

        # create dict of outputvar names with indexes for iteration
        outputvar_names = {
            ov.name: pos for pos, ov in enumerate(self.outputvar)
        }
        # extract dict of outputvar for manipulation
        outputvars = self.to_dict()['outputvar']

        if not append_output:
            self.output = list()
        else:
            # create dict of output names with indexes for iteration
            output_names = list()
            # modify existing output entries
            for pos, out in enumerate(self.output):
                output_names.append(out.id)
                self.output[pos].file.socket = False
                # Only change temporal_resolution if string, so not
                # specifically for each output
                if isinstance(temporal_resolution, str):
                    self.output[pos].file.timestep = temporal_resolution
                if out.id not in nonvariable_outputs:
                    self.output[pos].file.fmt = file_format
                    self.output[pos].file.name = (
                        f"{output_path}/{out.id}"
                        f".{available_formats[file_format]}"
                    )
                else:
                    self.output[pos].file.name = (
                        f"{output_path}/{out.id}"
                        f".{os.path.splitext(self.output[pos].file.name)[1]}"
                    )

        # handle each defined output
        for pos, out in enumerate(outputs):
            if out in outputvar_names and out not in output_names:

                # check if temporal resolution is defined for output
                if not temporal_resolution:
                    timestep = outputvars[outputvar_names[out]]['timestep']
                elif isinstance(temporal_resolution, list):
                    timestep = temporal_resolution[pos]
                else:
                    timestep = temporal_resolution

                # create new output entry
                new_out = self.__class__({
                    'id': outputvars[outputvar_names[out]]['name'],
                    'file': self.__class__({
                        'fmt': file_format,
                        'socket': False,
                        'timestep': timestep,
                        'name': f"{output_path}/"
                                f"{outputvars[outputvar_names[out]]['name']}"
                                f".{available_formats[file_format]}",
                    })
                })
                self.output.append(new_out)
            elif out not in outputvar_names:
                # raise error if defined outputs are not in outputvar
                raise ValueError(
                    f"The following output is not defined in outputvar: {out}"
                )

    def set_output_path(self, output_path):
        """Set output path of specified outputs
        :param output_path: path for outputs to be written, could also b
            relative path
        :type output_path: str
        """
        for out in self.output:
            file_name = out.file.name.split("/")
            file_name.reverse()
            out.file.name = f"{output_path}/{file_name[0]}"

    def get_startfrom(self):
        """Set restart file from which LPJmL starts the transient run
        """
        return self.restart_filename

    def set_startfrom(self, path=None, file_name=None):
        """Set restart file from which LPJmL starts the transient run
        """
        if path is not None:
            file_name = self.restart_filename.split("/")
            file_name.reverse()
            if self.nspinup < 1:
                self.restart_filename = (
                    f"{path}/restart_{self.firstyear-1}.lpj")
            else:
                self.restart_filename = f"{path}/{file_name[0]}"
        elif file_name is not None:
            file_check = file_name.split(".")
            file_check.reverse()
            if file_check[0] == 'lpj':
                self.restart_filename = file_name
        else:
            raise ValueError('Please provide either a path or a file_name.')

    def get_restart(self):
        """Set restart file from which LPJmL starts the transient run
        """
        return self.write_restart_filename

    def set_restart(self, path=None, file_name=None):
        """Set restart file from which LPJmL starts the transient run
        """
        if path is not None:
            file_name = self.write_restart_filename.split("/")
            file_name.reverse()
            if self.nspinup < 500:
                self.write_restart_filename = (
                    f"{path}/restart_{self.lastyear}.lpj")
            else:
                self.write_restart_filename = f"{path}/{file_name[0]}"
            self.restart_year = self.lastyear
        elif file_name is not None:
            file_check = file_name.split(".")
            file_check.reverse()
            if file_check[0] == 'lpj':
                self.write_restart_filename = file_name
        else:
            raise ValueError('Please provide either a path or a file_name.')

    def set_timerange(self,
                      start_year=1901,
                      end_year=2017,
                      write_start_year=None):
        """Set simulation time range, outputyear to start as a default here.
        :param start_year: start year of simulation
        :type start_year: int
        :param end_year: end year of simulation
        :type end_year: int
        :param write_start_year: first year of output being written
        :type write_start_year: int
        """
        self.firstyear = start_year
        if write_start_year:
            self.outputyear = write_start_year
        else:
            self.outputyear = start_year
        self.lastyear = end_year

    def set_coupler(self, inputs, outputs, model_name="copan:CORE"):
        """Coupled settings - no spinup, not write restart file and set sockets
        for inputs and outputs (via corresponding ids)
        :param inputs: list of inputs to be used as socket for coupling.
            Provide dictionary/json key as identifier -> entry in list.
        :type inputs: list
        :param outputs: list of outputs to be used as socket for coupling.
            Provide output id as identifier -> entry in list.
        :type outputs: list
        :param model_name: model name of the coupled program which also sets
            the model to coupled mode (without coupling coupled_model = None)
        :type model_name: str
        """
        self.write_restart = False
        self.nspinup = 0
        self.float_grid = True
        self.coupled_model = model_name
        self.set_input_sockets(inputs)
        self.set_output_sockets(outputs)

    def set_input_sockets(self, inputs=[]):
        """Set sockets for inputs and outputs (via corresponding ids)
        :param inputs: list of inputs to be used as socket for coupling.
            Provide dictionary/json key as identifier -> entry in list.
        :type inputs: list
        """
        for inp in inputs:
            sock_input = getattr(self.input, inp)
            if 'id' not in sock_input.__dict__.keys():
                raise ValueError('Please use a config with input ids.')
            if 'name' in sock_input.__dict__.keys():
                del sock_input.__dict__['name']
            sock_input.__dict__['fmt'] = 'sock'

    def set_output_sockets(self, outputs=[]):
        """Set sockets for inputs and outputs (via corresponding ids)

        :param outputs: list of outputs to be used as socket for coupling.
            Provide output id as identifier -> entry in list.
        :type outputs: list
        """
        if "grid" not in outputs:
            outputs.append("grid")

        # get names/ids only of outputs that are defined in outputvar
        valid_outs = {
            out.name for out in self.outputvar if out.name in outputs
        }

        # check if all outputs are valid
        nonvalid_outputs = list(set(outputs) - valid_outs)
        if nonvalid_outputs:
            raise ValueError(
                "The following outputs are not defined in outputvar: "
                f"{nonvalid_outputs}"
            )
        # get position of valid outputs in config output list
        output_pos = [
            pos for pos, out in enumerate(self.output) if out.id in valid_outs
        ]

        # set socket to true for corresponding outputs
        for pos in output_pos:
            if self.output[pos].id in valid_outs:
                self.output[pos].file.socket = True
                self.output[pos].file.timestep = "annual"

    def get_input_sockets(self):
        """get defined socket inputs as dict
        """
        inputs = self.input.to_dict()
        return {
            inp: inputs[inp] for inp in inputs if inputs[inp]["fmt"] == "sock"
        }

    def get_output_sockets(self):
        """get defined socket outputs as dict
        """
        outputs = self.to_dict()["output"]
        name_id = {out.name: out.id for out in self.outputvar}
        return {
            out["id"]: dict(
                {'index': name_id[out["id"]]}, **out
            ) for out in outputs if out["file"]["socket"]
        }


def parse_config(file_name="./lpjml.js", spin_up=False,
                 macros=None, config_class=False):
    """Precompile lpjml.js and return LpjmlConfig object or dict. Also
    evaluate macros. Analogous to R function `lpjmlKit::parse_config`.
    :param path: path to lpjml root
    :type path: str
    :param js_filename: js file filename, defaults to lpjml.js
    :type js_filename: str
    :param spin_up: convenience argument to set macro whether to start
        from restart file (`True`) or not (`False`). Defaults to `True`
    :type spin_up: bool
    :param macros: provide a macro in the form of "-DMACRO" or list of macros
    :type macros: str, list
    :param config_class: class of config object to be returned or None
        (return dict)
    :type config_class: class
    :return: if `return_dict == True` -> LpjmlConfig object, else a
        a dictionary
    :rtype: LpjmlConfig, dict
    """
    # precompile command
    cmd = ["cpp", "-P"]
    # add arguments
    if not spin_up:
        cmd.append('-DFROM_RESTART')
    if macros:
        if isinstance(macros, list):
            cmd.extend(macros)
        else:
            cmd.append(macros)
    cmd.append(file_name)

    # Subprocess call of cmd - return stdout
    json_str = subprocess.run(cmd, capture_output=True)

    # Convert to dict
    lpjml_config = json.loads(json_str.stdout, object_hook=config_class)

    return lpjml_config


def read_config(file_name, spin_up=False, macros=None, return_dict=False):
    """Read function for config files to be returned as LpjmlConfig object or
    alternatively dict.
    :param file_name: file name (including relative/absolute path) of the
        corresponding LPJmL configuration.
    :type file_name: str
    :param return_dict: if `True` an LpjmlConfig object is returned,
        else (`False`) a dictionary is returned
    :type return_dict: bool
    :return: if `return_dict == True` -> LpjmlConfig object, else a
        a dictionary
    :rtype: LpjmlConfig, dict
    """
    if not return_dict:
        config = SubConfig
    else:
        config = None

    # Try to read file as json
    try:
        with open(file_name) as file_con:
            lpjml_config = json.load(file_con, object_hook=config)

    # If not possible, precompile and parse JSON
    except json.decoder.JSONDecodeError:
        lpjml_config = parse_config(
            file_name, spin_up=spin_up, macros=macros, config_class=config
        )

    # Convert first level to LpjmlConfig object
    if not return_dict:
        lpjml_config.__class__ = LpjmlConfig

    return lpjml_config
