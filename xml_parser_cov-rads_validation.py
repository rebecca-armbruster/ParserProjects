import json, hashlib, re, os, sys, uuid
import pandas as pd
from datetime import datetime
from argparse import ArgumentParser
import xml.etree.ElementTree as et

required_parameters = {
    "Arztbrief/KIS Angaben": {
        "Arztbrief/KIS Angaben": [
            "Kohorte: Primäre Klasse",
            "Tage seit Aufnahme"
        ],
        "Patientenaufnahme": [
            "Aufnahme-Status zum Zeitpunkt der Bilderstellung (abhängig von der Anforderung)"
        ]
    },
    "CT": {
        "Qualitätsangaben und Protokoll": [
            "Nativ",
            "Pulmonalarteriell",
            "Arteriell",
            "Pulmonalarterielle und Arterielle Mischphase (Double-/Triple-Rule-Out)",
            "Portalvenös",
            "Spätvenös",
            "Art.-venöse Mischphase",
            "Bildqualität"
        ],
        "Intubation": [
            "Intubiert (in der aktuellen Bildgebung)"
        ],
        "Atelektase / Narbenstrang": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung",
            "Radiär (von zentral nach pleural)",
            "Kurvilinear (parallel zur Pleura)",
            "Kalkhaltig"
        ],
        "Konsolidierung": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung geographisch",
            "Führende Verteilung anatomisch",
            "Subpleurale Aussparung",
            "Mit Einschmelzung",
            "Kalkhaltig"
        ],
        "Milchglasareal": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung geographisch",
            "Führende Verteilung anatomisch",
            "Konsolidierungen innerhalb des Milchgasareals",
            "Gefäßverdickung/Hyperämie",
            "Subpleurale Aussparung",
            "Mit Crazy-paving",
            "Mit Reversed Halo",
            "Mit Vakuolenzeichen"
        ],
        "Emphysem": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung",
            "Bullös",
            "Paraseptal"
        ],
        "Retikulation": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung geographisch",
            "Führende Verteilung anatomisch",
            "Subpleurale Aussparung",
            "Mit Honeycombing"
        ],
        "Kavitation": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Mit Spiegelbildung",
            "Mit Luftsichel / Air-Crescent-Zeichen",
            "Mit Halo",
            "Dünnwandig / zystisch"
        ],
        "Raumforderung > 30 mm": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Kalkhaltig",
            "Mit Umgebungsinfiltration",
            "Mit Einschmelzung",
            "Mit Halo"
        ],
        "Rundherd / Knoten 5-30 mm": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung geographisch",
            "Führende Verteilung anatomisch",
            "Nicht-solide",
            "Mit Einschmelzung",
            "Kalkhaltig",
            "Unscharf / mit Halo"
        ],
        "Bronchuswandverdickungen": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung"
        ],
        "Bronchiektasen": [
            "Lokalisation Lappen",
            "Schweregrad (Oberlappen rechts)",
            "Schweregrad (Mittellappen rechts)",
            "Schweregrad (Unterlappen rechts)",
            "Schweregrad (Oberlappen links)",
            "Schweregrad (Lingula)",
            "Schweregrad (Unterlappen links)",
            "Führende Verteilung",
            "Mucus Plugging",
            "Mit Traktion"
        ],
        "Pneumothorax": [
            "Lokalisation Seite",
            "Schweregrad (links)",
            "Schweregrad (rechts)"
        ],
        "Pleuraerguss": [
            "Lokalisation Seite",
            "Schweregrad (links)",
            "Schweregrad (rechts)",
            "Hyperdens (>20HU)",
            "Gefangen"
        ],
        "Pleuraerkrankung": [
            "Lokalisation Seite",
            "Führende Verteilung",
            "Kalkhaltig"
        ],
        "Mediastinum": [
            "Lymphadenopathie / Tumor",
            "Lokalisation",
            "Perikarderguss"
        ],
        "Dominante Pathologien": [
            "1. dominante Pathologie",
            "2. dominante Pathologie",
            "3. dominante Pathologie"
        ],
        "Beurteilung": [
            "COV-RADS Klassifikation*"
        ]
    },
    "Klinisch-anamnestische Information": {
        "Demographische Informationen": [
            "Alter",
            "Geschlecht"
        ],
        "Bekannte Exposition": [
            "Bekannte Exposition gegenüber infizierten Personen"
        ],
        "Komorbiditäten aus Arztbrief": [
            "Immunsuppression",
            "Andere Komorbiditäten"
        ],
        "Klinische Symptome": [
            "Ist die Dokumentation von klinischen Symptomen erwünscht?",
            "Beginn der klinischen Symptome",
            "Fieber",
            "Atemfrequenz",
            "Syst. RR",
            "Sauerstoff-Sättigung",
            "Oxygenierungsindex pO2/FiO2",
            "Respiratorische Symptomatik",
            "Neurologische Symptomatik",
            "Abdominelle Symptomatik",
            "Kardiale Symptomatik"
        ]
    },
    "Laborparameter": {
        "Laborparameter": ["Labordaten: Erhebungsdatum"],
        "Virologie": [
            "COVID-PCR Status",
            "Datum des aktuellsten RT-PCR-Tests",
            "Datum des vorherigen RT-PCR-Tests"
        ]
    }
}


def get_cases(r):
    """ Get a list of all cases in an XML file with root r.
    
    Args:
        r: root of the XML file
    
    Returns:
        list: List of all cases.
    """
    return [case for trial in r.iter('Trial')
            for trial_arm in trial.iter('TrialArm')
            for case in trial_arm.iter('Case')]


def create_dataframe(params):
    """ Create dataframe for collecting patient information.
    
    Args:
        params: Dictionary containing the names of the required parameters.
        
    Returns:
        pd.Dataframe: Empty dataframe for case information.
    
    """
    data_dict = {'PatientID': [], 'Template': []}
    for template in list(params):
        for group in params[template]:
            for question in params[template][group]:
                data_dict.update({f'{template}//{group}::{question}': []})
    return pd.DataFrame(data_dict)


def encrypt_id(s):
    hash_object = hashlib.sha256(s.encode())
    hash_string = hash_object.hexdigest()
    return hash_string


def clean_template_name(t, to_replace='RACOON COVID-19 '):
    t = t.replace(to_replace, '')
    re_digit = re.compile(r'\([0-9]*\)')
    search_digit = re_digit.search(t)
    if search_digit:
        t = t.replace(f' {search_digit[0]}', '')
    return t


def extract_date(s, regex=r'\d{4}-\d{2}-\d{2}', str_pattern='%Y-%m-%d', return_string=False):
    try:
        match = re.search(regex, s)
        return match.group() if return_string else datetime.strptime(match.group(), str_pattern).date()
    except TypeError:
        return s


def get_column_name_by_template(template, params='required_parameters.json'):
    """ Get all column names  that belong to the given template, according to the given required_parameters.

    Args:
        template: Name of the template to obtain column names for.
        params: Either string with path to load the required_parameters from JSON file or dictionary containing all
                required parameters.

    Returns:
        list: List of all column names that belong to the given template.
    """
    if isinstance(params, str):
        with open(params, encoding='utf-8') as json_file:
            params = json.load(json_file)
    return [f'{template}//{group}::{question}' for group in params[template] for question in params[template][group]]


def get_column_order(template_order, params='required_parameters.json'):
    if isinstance(params, str):
        with open(params, encoding='utf-8') as json_file:
            params = json.load(json_file)
    return [column for template in template_order for column in get_column_name_by_template(template, params)]


def get_template_information(d, c, params, anonymization='UUID4'):
    """ Extract all template information for a given case.
    
    Args:
        d: Dataframe containing information about previous cases.
        c: Current case (XML element)
        params: Dictionary containing the names of the required parameters.
        anonymization: Indicating whether to use SHA256 encryption or random UUIDs.
        
    Returns:
        pd.DataFrame: Dataframe containing update case information
    
    """
    if anonymization == 'SHA256':
        patient_id = c.attrib['CaseID'] + c[0].attrib['LastName'] + c[0].attrib['PatientID'] + c[0].attrib[
            'InstitutionName']
        patient_id = encrypt_id(str(patient_id))
    elif anonymization == 'UUID4':
        patient_id = uuid.uuid4()
    templates = list(c.iter('Task'))
    for j, template in enumerate(templates):
        try:
            template_name = clean_template_name(template.attrib['Header'])
            template_dict = {'PatientID': patient_id, 'Template': template_name}
            for group in template.iter('Group'):
                group_name = group.attrib['Header']
                if group_name in params[template_name]:
                    for question in group.iter('Question'):
                        question_name = question.attrib['Question']
                        # if question_name == 'Alter':
                        #     print(question_name)
                        if question_name in params[template_name][group_name]:
                            answer_name = question.attrib['Answer']
                            template_dict.update({f'{template_name}//{group_name}::{question_name}': answer_name})
            d = d.append(template_dict, ignore_index=True)
        except KeyError:
            template_name = clean_template_name(template.attrib['Header'])
            if template_name not in ['Behandlungsplan', 'Röntgen']:
                print(f'ERROR::KeyError with key {template_name}')
        # d = d.append(template_dict, ignore_index=True)
    return d


def main(input_file='20211104_Mint_Export.xml',
         required_parameters='required_parameters.json',
         anonymization='UUID4', template_order=None):
    # with open(required_parameters_file, encoding='utf-8') as json_file:
    #     required_parameters = json.load(json_file)
    if isinstance(required_parameters, str):
        with open(required_parameters, encoding='utf-8') as json_file:
            required_parameters = json.load(json_file)

    print('INFO::Extracting tree and root objects from XML file')
    tree = et.parse(input_file)
    root = tree.getroot()

    all_cases = get_cases(root)
    n_cases = len(all_cases)

    data = create_dataframe(params=required_parameters)

    print(f'INFO::Extracting case information')
    for i, case in enumerate(all_cases):
        if i % 50 == 0:
            print(f'INFO::Currently handling case: {i + 1}/{n_cases}')
        data = get_template_information(d=data, c=case, params=required_parameters, anonymization=anonymization)

    info = 'all'
    print("INFO::Data won't be filtered for certain patients")

    if template_order is not None:
        data = data[['PatientID', 'Template'] + get_column_order(template_order, params=required_parameters)]

    return data, info


if __name__ == '__main__':
    print('START::XML extraction started. This might take up to a few minutes...')

    args = {'anonymization': 'UUID4'}
    print('INFO::Given arguments:')
    for k, v in args.items():
        print('\t', k, '->', v)

    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    print(f'INFO::Current working directory: {script_dir}')
    xml_files = [file for file in os.listdir(script_dir) if '.xml' in file]

    if len(xml_files) > 0:
        print(f'INFO::Processing file {xml_files[0]}')
        start = datetime.now()
        template_order = ['Arztbrief/KIS Angaben', 'Klinisch-anamnestische Information', 'Laborparameter', 'CT']
        data, info = main(input_file=xml_files[0], required_parameters=required_parameters, template_order=template_order, **args)

        print('INFO::Save excel file')
        out_file = os.path.join(script_dir, f'{info}_raw_data_cov-rads-validation.xlsx',)
        data.to_excel(out_file, index=False)

        print('DONE::XML extraction finished')

        stop = datetime.now()
        print(f'INFO::Total operation time: {stop - start}')
    else:
        print('INFO::No XML files found in this directory. Stop processing.')
    input('TODO::Press enter to close this window.')
