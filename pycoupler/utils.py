import os
import json
from subprocess import run, Popen, PIPE, CalledProcessError
from fuzzywuzzy import fuzz, process


def clone_lpjml(model_location=".", branch="lpjml53_copan"):
    """Git clone lpjml via oauth using git url and token provided as
    environment variables. If copan implementation still on branch use branch
    argument.
    :param model_location: location to `git clone` lpjml -> LPJmL_internaö
    :type model_location: str
    :param branch: switch/`git checkout` to branch with copan implementation.
        Defaults to "lpjml53_copan".
    :type branch: str
    """
    git_url = os.environ.get("GIT_LPJML_URL")
    git_token = os.environ.get("GIT_READ_TOKEN")
    cmd = ["git", "clone", f"https://oauth2:{git_token}@{git_url}"]
    with Popen(
        cmd, stdout=PIPE, bufsize=1, universal_newlines=True,
        cwd=model_location
    ) as p:
        for line in p.stdout:
            print(line, end='')
    # raise error if returncode does not reflect successfull call
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
    # check if branch required
    if branch:
        with Popen(
            ["git", "checkout", branch],
            stdout=PIPE, bufsize=1, universal_newlines=True,
            cwd=f"{model_location}/LPJmL_internal"
        ) as p:
            for line in p.stdout:
                print(line, end='')


def compile_lpjml(model_path=".", make_fast=False, make_clean=False):
    """Compile or make lpjml after model clone/changes. make_fast for small
    changes, make_clean to delete previous compiled version (clean way)
    :param model_path: path to `LPJmL_internal` (lpjml repository)
    :type model_path: str
    :param make_fast: make with arg -j8. Defaults to False.
    :type make_fast: bool
    :param make_clean: delete previous compiled model version. Defaults to
        False.
    :type make_clean: bool
    """
    if not os.path.isdir(model_path):
        raise ValueError(
            f"Folder of model_path '{model_path}' does not exist!"
        )
    if not os.path.isfile(f"{model_path}/bin/lpjml"):
        proc_status = run(
            "./configure.sh", capture_output=True, cwd=model_path
        )
        print(proc_status.stdout.decode('utf-8'))
    # make clean first
    if make_clean:
        run(["make", "clean"], capture_output=True, cwd=model_path)
    # make all call with possibility to make fast via -j8 arg
    cmd = ['make']
    if make_fast:
        cmd.append('-j16')
    cmd.append('all')
    # open process to be iteratively printed to the console
    with Popen(
        cmd, stdout=PIPE, bufsize=1, universal_newlines=True, cwd=model_path
    ) as p:
        for line in p.stdout:
            print(line, end='')
    # raise error if returncode does not reflect successfull call
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


def check_lpjml(config_file, model_path):
    """Check if config file is set correctly.
    :param config_file: file_name (including path) to generated config json
        file.
    :type model_path: str
    :param model_path: path to `LPJmL_internal` (lpjml repository)
    :type model_path: str
    """
    if not os.path.isdir(model_path):
        raise ValueError(
            f"Folder of model_path '{model_path}' does not exist!"
        )
    if os.path.isfile(f"{model_path}/bin/lpjcheck"):
        proc_status = run(
            ["./bin/lpjcheck", config_file], capture_output=True,  # "-param",
            cwd=model_path
        )
    if proc_status.returncode == 0:
        print(proc_status.stdout.decode('utf-8'))
    else:
        print(proc_status.stdout.decode('utf-8'))
        print(proc_status.stderr.decode('utf-8'))


def get_countries():
    """Current workaround to get countries defined in LPJmL.
    """
    return {
        "Afghanistan": {"name": "Afghanistan", "code": "AFG"},
        "Aland_Islands": {"name": "Aland Islands", "code": "ALA"},
        "Albania": {"name": "Albania", "code": "ALB"},
        "Algeria": {"name": "Algeria", "code": "DZA"},
        "American_Samoa": {"name": "American Samoa", "code": "ASM"},
        "Angola": {"name": "Angola", "code": "AGO"},
        "Anguilla": {"name": "Anguilla", "code": "AIA"},
        "Antigua_and_Barbuda": {"name": "Antigua and Barbuda", "code": "ATG"},
        "Argentina": {"name": "Argentina", "code": "ARG"},
        "Armenia": {"name": "Armenia", "code": "ARM"},
        "Austria": {"name": "Austria", "code": "AUT"},
        "Azerbaijan": {"name": "Azerbaijan", "code": "AZE"},
        "Bahamas_The": {"name": "Bahamas,The", "code": "BHS"},
        "Bahrain": {"name": "Bahrain", "code": "BHR"},
        "Bangladesh": {"name": "Bangladesh", "code": "BGD"},
        "Barbados": {"name": "Barbados", "code": "BRB"},
        "Belgium": {"name": "Belgium", "code": "BEL"},
        "Belize": {"name": "Belize", "code": "BLZ"},
        "Benin": {"name": "Benin", "code": "BEN"},
        "Bermuda": {"name": "Bermuda", "code": "BMU"},
        "Bhutan": {"name": "Bhutan", "code": "BTN"},
        "Bolivia": {"name": "Bolivia", "code": "BOL"},
        "Bosnia_and_Herzegovina": {
            "name": "Bosnia and Herzegovina", "code": "BIH"
        },
        "Botswana": {"name": "Botswana", "code": "BWA"},
        "British_Indian_Ocean_Territory": {
            "name": "British Indian Ocean Territory", "code": "IOT"
        },
        "Brunei": {"name": "Brunei", "code": "BRN"},
        "Bulgaria": {"name": "Bulgaria", "code": "BGR"},
        "Burkina_Faso": {"name": "Burkina Faso", "code": "BFA"},
        "Burundi": {"name": "Burundi", "code": "BDI"},
        "Byelarus": {"name": "Byelarus", "code": "BLR"},
        "Cambodia": {"name": "Cambodia", "code": "KHM"},
        "Cameroon": {"name": "Cameroon", "code": "CMR"},
        "Cape_Verde": {"name": "Cape Verde", "code": "CPV"},
        "Cayman_Islands": {"name": "Cayman Islands", "code": "CYM"},
        "Central_African_Republic": {
            "name": "Central African Republic", "code": "CAF"
        },
        "Chad": {"name": "Chad", "code": "TCD"},
        "Chile": {"name": "Chile", "code": "CHL"},
        "Christmas_Island": {"name": "Christmas Island", "code": "CXR"},
        "Cocos_Keeling_Islands": {
            "name": "Cocos Keeling Islands", "code": "CCK"
        },
        "Colombia": {"name": "Colombia", "code": "COL"},
        "Comoros": {"name": "Comoros", "code": "COM"},
        "Congo_Brazzaville": {"name": "Congo-Brazzaville", "code": "COG"},
        "Cook_Islands": {"name": "Cook Islands", "code": "COK"},
        "Costa_Rica": {"name": "Costa Rica", "code": "CRI"},
        "Croatia": {"name": "Croatia", "code": "HRV"},
        "Cuba": {"name": "Cuba", "code": "CUB"},
        "Curacao": {"name": "Curacao", "code": "CUW"},
        "Cyprus": {"name": "Cyprus", "code": "CYP"},
        "Czech_Republic": {"name": "Czech Republic", "code": "CZE"},
        "Denmark": {"name": "Denmark", "code": "DNK"},
        "Djibouti": {"name": "Djibouti", "code": "DJI"},
        "Dominica": {"name": "Dominica", "code": "DMA"},
        "Dominican_Republic": {"name": "Dominican Republic", "code": "DOM"},
        "Ecuador": {"name": "Ecuador", "code": "ECU"},
        "Egypt": {"name": "Egypt", "code": "EGY"},
        "El_Salvador": {"name": "El Salvador", "code": "SLV"},
        "Equatorial_Guinea": {"name": "Equatorial Guinea", "code": "GNQ"},
        "Eritrea": {"name": "Eritrea", "code": "ERI"},
        "Estonia": {"name": "Estonia", "code": "EST"},
        "Ethiopia": {"name": "Ethiopia", "code": "ETH"},
        "Falkland_Islands_or_Islas_Malvinas": {
            "name": "Falkland Islands or Islas Malvinas", "code": "FLK"
        },
        "Faroe_Islands": {"name": "Faroe Islands", "code": "FRO"},
        "Federated_States_of_Micronesia": {
            "name": "Federated States of Micronesia", "code": "FSM"
        },
        "Fiji": {"name": "Fiji", "code": "FJI"},
        "Finland": {"name": "Finland", "code": "FIN"},
        "France": {"name": "France", "code": "FRA"},
        "French_Guiana": {"name": "French Guiana", "code": "GUF"},
        "French_Polynesia": {"name": "French Polynesia", "code": "PYF"},
        "French_Southern_and_Antarctica_Lands": {
            "name": "French Southern and Antarctica Lands", "code": "NOC"
            },
        "Gabon": {"name": "Gabon", "code": "GAB"},
        "Gambia_The": {"name": "Gambia,The", "code": "GMB"},
        "Georgia": {"name": "Georgia", "code": "GEO"},
        "Germany": {"name": "Germany", "code": "DEU"},
        "Ghana": {"name": "Ghana", "code": "GHA"},
        "Greece": {"name": "Greece", "code": "GRC"},
        "Greenland": {"name": "Greenland", "code": "GRL"},
        "Grenada": {"name": "Grenada", "code": "GRD"},
        "Guadeloupe": {"name": "Guadeloupe", "code": "GLP"},
        "Guam": {"name": "Guam", "code": "GUM"},
        "Guatemala": {"name": "Guatemala", "code": "GTM"},
        "Guernsey": {"name": "Guernsey", "code": "GGY"},
        "Guinea_Bissau": {"name": "Guinea-Bissau", "code": "GNB"},
        "Guinea": {"name": "Guinea", "code": "GIN"},
        "Guyana": {"name": "Guyana", "code": "GUY"},
        "Haiti": {"name": "Haiti", "code": "HTI"},
        "Heard_Island_and_McDonald_Islands": {
            "name": "Heard Island and McDonald Islands", "code": "HMD"
        },
        "Honduras": {"name": "Honduras", "code": "HND"},
        "Hong_Kong": {"name": "Hong Kong", "code": "HKG"},
        "Hungary": {"name": "Hungary", "code": "HUN"},
        "Iceland": {"name": "Iceland", "code": "ISL"},
        "Indonesia": {"name": "Indonesia", "code": "IDN"},
        "Iran": {"name": "Iran", "code": "IRN"},
        "Iraq": {"name": "Iraq", "code": "IRQ"},
        "Ireland": {"name": "Ireland", "code": "IRL"},
        "Isle_of_Man": {"name": "Isle of Man", "code": "IMN"},
        "Israel": {"name": "Israel", "code": "ISR"},
        "Italy": {"name": "Italy", "code": "ITA"},
        "Ivory_Coast": {"name": "Ivory Coast", "code": "CIV"},
        "Jamaica": {"name": "Jamaica", "code": "JAM"},
        "Japan": {"name": "Japan", "code": "JPN"},
        "Jersey": {"name": "Jersey", "code": "JEY"},
        "Jordan": {"name": "Jordan", "code": "JOR"},
        "Kazakhstan": {"name": "Kazakhstan", "code": "KAZ"},
        "Kenya": {"name": "Kenya", "code": "KEN"},
        "Kiribati": {"name": "Kiribati", "code": "KIR"},
        "Kosovo": {"name": "Kosovo", "code": "KO-"},
        "Kuwait": {"name": "Kuwait", "code": "KWT"},
        "Kyrgyzstan": {"name": "Kyrgyzstan", "code": "KGZ"},
        "Laos": {"name": "Laos", "code": "LAO"},
        "Latvia": {"name": "Latvia", "code": "LVA"},
        "Lebanon": {"name": "Lebanon", "code": "LBN"},
        "Lesotho": {"name": "Lesotho", "code": "LSO"},
        "Liberia": {"name": "Liberia", "code": "LBR"},
        "Libya": {"name": "Libya", "code": "LBY"},
        "Lithuania": {"name": "Lithuania", "code": "LTU"},
        "Luxembourg": {"name": "Luxembourg", "code": "LUX"},
        "Macedonia": {"name": "Macedonia", "code": "MKD"},
        "Madagascar": {"name": "Madagascar", "code": "MDG"},
        "Malawi": {"name": "Malawi", "code": "MWI"},
        "Malaysia": {"name": "Malaysia", "code": "MYS"},
        "Maldives": {"name": "Maldives", "code": "MDV"},
        "Mali": {"name": "Mali", "code": "MLI"},
        "Malta": {"name": "Malta", "code": "MLT"},
        "Marshall Islands": {"name": "Marshall Islands", "code": "MHL"},
        "Martinique": {"name": "Martinique", "code": "MTQ"},
        "Mauritania": {"name": "Mauritania", "code": "MRT"},
        "Mauritius": {"name": "Mauritius", "code": "MUS"},
        "Mayotte": {"name": "Mayotte", "code": "MYT"},
        "Mexico": {"name": "Mexico", "code": "MEX"},
        "Moldova": {"name": "Moldova", "code": "MDA"},
        "Mongolia": {"name": "Mongolia", "code": "MNG"},
        "Montenegro": {"name": "Montenegro", "code": "MNE"},
        "Montserrat": {"name": "Montserrat", "code": "MSR"},
        "Morocco": {"name": "Morocco", "code": "MAR"},
        "Mozambique": {"name": "Mozambique", "code": "MOZ"},
        "Myanmar or Burma": {"name": "Myanmar or Burma", "code": "MMR"},
        "Namibia": {"name": "Namibia", "code": "NAM"},
        "Nauru": {"name": "Nauru", "code": "NRU"},
        "Nepal": {"name": "Nepal", "code": "NPL"},
        "Netherlands": {"name": "Netherlands", "code": "NLD"},
        "New Caledonia": {"name": "New Caledonia", "code": "NCL"},
        "New Zealand": {"name": "New Zealand", "code": "NZL"},
        "Nicaragua": {"name": "Nicaragua", "code": "NIC"},
        "Niger": {"name": "Niger", "code": "NER"},
        "Nigeria": {"name": "Nigeria", "code": "NGA"},
        "Niue": {"name": "Niue", "code": "NIU"},
        "No Land": {"name": "No Land", "code": "XNL"},
        "Norfolk Island": {"name": "Norfolk Island", "code": "NFK"},
        "North Korea": {"name": "North Korea", "code": "PRK"},
        "Northern Mariana Islands": {
            "name": "Northern Mariana Islands", "code": "MNP"
        },
        "Norway": {"name": "Norway", "code": "NOR"},
        "Oman": {"name": "Oman", "code": "OMN"},
        "Pakistan": {"name": "Pakistan", "code": "PAK"},
        "Palau": {"name": "Palau", "code": "PLW"},
        "Panama": {"name": "Panama", "code": "PAN"},
        "Papua New Guinea": {"name": "Papua New Guinea", "code": "PNG"},
        "Paraguay": {"name": "Paraguay", "code": "PRY"},
        "Peru": {"name": "Peru", "code": "PER"},
        "Philippines": {"name": "Philippines", "code": "PHL"},
        "Pitcairn Islands": {"name": "Pitcairn Islands", "code": "PCN"},
        "Poland": {"name": "Poland", "code": "POL"},
        "Portugal": {"name": "Portugal", "code": "PRT"},
        "Puerto Rico": {"name": "Puerto Rico", "code": "PRI"},
        "Qatar": {"name": "Qatar", "code": "QAT"},
        "Reunion": {"name": "Reunion", "code": "REU"},
        "Romania": {"name": "Romania", "code": "ROU"},
        "Rwanda": {"name": "Rwanda", "code": "RWA"},
        "Saint Helena Ascension and Tristan da Cunha": {
            "name": "Saint Helena Ascension and Tristan da Cunha",
            "code": "SHN"
        },
        "Saint Kitts and Nevis": {
            "name": "Saint Kitts and Nevis", "code": "KNA"
        },
        "Saint Lucia": {"name": "Saint Lucia", "code": "LCA"},
        "Saint Pierre and Miquelon": {
            "name": "Saint Pierre and Miquelon", "code": "SPM"
        },
        "Sao Tome and Principe": {
            "name": "Sao Tome and Principe", "code": "STP"
        },
        "Saudi Arabia": {"name": "Saudi Arabia", "code": "SAU"},
        "Senegal": {"name": "Senegal", "code": "SEN"},
        "Serbia": {"name": "Serbia", "code": "SRB"},
        "Seychelles": {"name": "Seychelles", "code": "SYC"},
        "Sierra Leone": {"name": "Sierra Leone", "code": "SLE"},
        "Singapore": {"name": "Singapore", "code": "SGP"},
        "Slovakia": {"name": "Slovakia", "code": "SVK"},
        "Slovenia": {"name": "Slovenia", "code": "SVN"},
        "Solomon Islands": {"name": "Solomon Islands", "code": "SLB"},
        "Somalia": {"name": "Somalia", "code": "SOM"},
        "South Africa": {"name": "South Africa", "code": "ZAF"},
        "South Georgia and the South Sandwich Islands": {
            "name": "South Georgia and the South Sandwich Islands",
            "code": "SGS"
        },
        "South Korea": {"name": "South Korea", "code": "KOR"},
        "South Sudan": {"name": "South Sudan", "code": "SSD"},
        "Spain": {"name": "Spain", "code": "ESP"},
        "Sri Lanka": {"name": "Sri Lanka", "code": "LKA"},
        "St. Vincent and the Grenadines": {
            "name": "St. Vincent and the Grenadines", "code": "VCT"
        },
        "Sudan": {"name": "Sudan", "code": "SDN"},
        "Suriname": {"name": "Suriname", "code": "SUR"},
        "Svalbard": {"name": "Svalbard", "code": "SJM"},
        "Swaziland": {"name": "Swaziland", "code": "SWZ"},
        "Sweden": {"name": "Sweden", "code": "SWE"},
        "Switzerland": {"name": "Switzerland", "code": "CHE"},
        "Syria": {"name": "Syria", "code": "SYR"},
        "Taiwan": {"name": "Taiwan", "code": "TWN"},
        "Tajikistan": {"name": "Tajikistan", "code": "TJK"},
        "Tanzania, United Republic of": {
            "name": "Tanzania, United Republic of", "code": "TZA"
        },
        "Thailand": {"name": "Thailand", "code": "THA"},
        "Timor-Leste": {"name": "Timor-Leste", "code": "TLS"},
        "Togo": {"name": "Togo", "code": "TGO"},
        "Tokelau": {"name": "Tokelau", "code": "TKL"},
        "Tonga": {"name": "Tonga", "code": "TON"},
        "Trinidad and Tobago": {"name": "Trinidad and Tobago", "code": "TTO"},
        "Tunisia": {"name": "Tunisia", "code": "TUN"},
        "Turkey": {"name": "Turkey", "code": "TUR"},
        "Turkmenistan": {"name": "Turkmenistan", "code": "TKM"},
        "Turks and Caicos Islands": {
            "name": "Turks and Caicos Islands", "code": "TCA"
        },
        "Tuvalu": {"name": "Tuvalu", "code": "TUV"},
        "Uganda": {"name": "Uganda", "code": "UGA"},
        "Ukraine": {"name": "Ukraine", "code": "UKR"},
        "United Arab Emirates": {
            "name": "United Arab Emirates", "code": "ARE"
        },
        "United Kingdom": {"name": "United Kingdom", "code": "GBR"},
        "United States Minor Outlying Islands": {
            "name": "United States Minor Outlying Islands", "code": "UMI"
        },
        "Uruguay": {"name": "Uruguay", "code": "URY"},
        "Uzbekistan": {"name": "Uzbekistan", "code": "UZB"},
        "Vanuatu": {"name": "Vanuatu", "code": "VUT"},
        "Venezuela": {"name": "Venezuela", "code": "VEN"},
        "Vietnam": {"name": "Vietnam", "code": "VNM"},
        "Virgin Islands": {"name": "Virgin Islands", "code": "VGB"},
        "Wallis and Futuna": {"name": "Wallis and Futuna", "code": "WLF"},
        "West Bank": {"name": "West Bank", "code": "PSE"},
        "Western Sahara": {"name": "Western Sahara", "code": "ESH"},
        "Western Samoa": {"name": "Western Samoa", "code": "WSM"},
        "Yemen": {"name": "Yemen", "code": "YEM"},
        "Zaire, DR Congo": {"name": "Zaire, DR Congo", "code": "COD"},
        "Zambia": {"name": "Zambia", "code": "ZMB"},
        "Zimbabwe": {"name": "Zimbabwe", "code": "ZWE"},
        "Australia": {"name": "Australia", "code": "AUS"},
        "Brazil": {"name": "Brazil", "code": "BRA"},
        "Canada": {"name": "Canada", "code": "CAN"},
        "China": {"name": "China", "code": "CHN"},
        "India": {"name": "India", "code": "IND"},
        "Russia": {"name": "Russia", "code": "RUS"},
        "United States": {"name": "United States of America", "code": "USA"}
    }


def search_country(query):
    """Search for countries based on a fuzzy matching algorithm.
    :param query: The search query.
    :type query: str
    :return: The matching country code.
    :rtype: str
    """
    countries = get_countries()
    name, _ = process.extractOne(query, countries.keys(), scorer=fuzz.ratio)
    return countries[name]['code']


def read_json(file_name, object_hook=None):
    with open(file_name) as file_con:
        json_dict = json.load(file_con, object_hook=object_hook)

    return json_dict


def create_subdirs(base_path):
    """Check if config file is set correctly.
    :param base_path: directory to check wether required subfolders exists. If
        not create corresponding folder (input, output, restart)
    :type base_path: str
    """
    if not os.path.exists(base_path):
        raise OSError(f"Path '{base_path}' does not exist.")

    if not os.path.exists(f"{base_path}/input"):
        os.makedirs(f"{base_path}/input")
        print(f"Input path '{base_path}/input' was created.")

    if not os.path.exists(f"{base_path}/output"):
        os.makedirs(f"{base_path}/output")
        print(f"Output path '{base_path}/output' was created.")

    if not os.path.exists(f"{base_path}/restart"):
        os.makedirs(f"{base_path}/restart")
        print(f"Restart path '{base_path}/restart' was created.")

    return base_path
