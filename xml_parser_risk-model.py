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
        ],
        "Outcome Parameter": [
            "Datum der letzten Eintragung KIS",
            "Die letzte dokumentierte Patientenoutcomeerfassung beschreibt",
            "Innerhalb des erfassten Aufenthaltes war der höchste Behandlungsstatus"
        ]
    },
    "Behandlungsplan": {
        "Behandlungsplan": [
            "Behandlungsplan: Erhebungsdatum"
        ],
        "Behandlungsprotokoll": [
            "Sauerstofftherapie",
            "Sauerstofftherapie: Art",
            "Sauerstofftherapie: Details",
            "Andere Therapie"
        ]
    },
    "CT": {
        "Intubation": [
            "Intubiert (in der aktuellen Bildgebung)"
        ],
        "Gesamtbeurteilung": [
            "Lungenparenchym"
        ],
        "Lungenparenchym Pathologien": [
            "Konsolidierungen",
            "Milchglasareal"
        ],
        "Bronchi Pathologien": [
            "Bronchuswandverdickungen"
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
        "Dominante Pathologien": [
            "1. dominante Pathologie",
            "2. dominante Pathologie",
            "3. dominante Pathologie"
        ],
        "Severity Scores": [
            "SARS Lungen-CT Score",
            "Lunge Oberfeld links",
            "Lunge Mittelfeld links",
            "Lunge Unterfeld links",
            "Lunge Oberfeld rechts",
            "Lunge Mittelfeld rechts",
            "Lunge Unterfeld rechts",
            "Lungen-CT Gesamtscore"
        ],
        "Sonstiges": [
            "Lungenparenchym: ergänzende Angaben",
            "COVID spezifische Angaben: ergänzende Angaben",
            "Weitere Auffälligkeiten",
            "Weitere Auffälligkeiten: Details"
        ],
        "Beurteilung": [
            "COVID-19 CT-morphologische Klassifikation",
            "CO-RADS Klassifikation",
            "COV-RADS Klassifikation*",
            "Klassifikation des Lungenbefalls",
            "Ausdehnung der Pneumonie",
            "Bei passender klinischer Korrelation ist der Lungenbefall bildmorphologisch mit ARDS",
            "CT-Veränderungen des Lungenparenchyms vereinbar mit"
        ],
        "Verlaufsbeurteilung": [
            "Lungenbeteiligung im Verlauf",
            "Verlaufsbeurteilung der Milchglasareale",
            "Verlaufsbeurteilung der Konsolidierungen",
            "Verlaufsbeurteilung der fibrotischen Veränderungen",
            "Andere Veränderungen zur Voruntersuchung"
        ],
        "Referenzmessungen": [
            "Digitale Stanze Luft (prästernale Höhe)"
        ]
    },
    "Klinisch-anamnestische Information": {
        "Komorbiditäten aus Arztbrief": [
            "Emphysem",
            "Lungenfibrose",
            "Gibt es andere bekannte Komorbiditäten?",
            "Tabak rauchen",
            "Pack years",
            "Chronisch obstruktive Lungenerkrankung",
            "Andere Lungenerkrankungen",
            "Bluthochdruck",
            "Herzerkrankungen",
            "Stauung/Ödem",
            "Dialyse",
            "Diabetes mellitus",
            "Insulintherapie ",
            "Andere Komorbiditäten"
        ],
        "Klinische Symptome": [
            "Atemfrequenz",
            "Syst. RR",
            "Sauerstoff-Sättigung",
            "Oxygenierungsindex pO2/FiO2"
        ]
    },
    "Laborparameter": {
        "Laborparameter": [
            "Labordaten: Erhebungsdatum"
        ],
        "Blutbild": [
            "Lymphozyten",
            "Lymphozyten: Wert"
        ],
        "Entzündungsparameter": [
            "High-sensitivity C-reactive protein (hs-CRP)",
            "High-sensitivity C-reactive protein (hs-CRP): Wert",
            "Interleukin-6 (IL-6)",
            "Interleukin-6 (IL-6): Wert"
        ],
        "Gerinnungsfunktion": [
            "D-Dimer",
            "D-Dimer: Wert"
        ],
        "Andere Laborparameter": [
            "Andere Laborparameter"
        ]
    },
    "Röntgen": {
        "Intubation": [
            "Intubiert (in der aktuellen Bildgebung)"
        ],
        "Gesamtbeurteilung": [
            "Lungenparenchym"
        ],
        "Lungenparenchym Pathologien": [
            "Konsolidierungen",
            "Milchglastrübung"
        ]
    }
}


def extract_date(s, regex=r'\d{4}-\d{2}-\d{2}', str_pattern='%Y-%m-%d', return_string=False):
    try:
        match = re.search(regex, s)
        return match.group() if return_string else datetime.strptime(match.group(), str_pattern).date()
    except TypeError:
        return s


def encrypt_id(s):
    hash_object = hashlib.sha256(s.encode())
    hash_string = hash_object.hexdigest()
    return hash_string


def clean_template_name(t):
    t = t.replace('RACOON COVID-19 ', '')
    re_digit = re.compile(r'\([0-9]*\)')
    search_digit = re_digit.search(t)
    if search_digit:
        t = t.replace(f' {search_digit[0]}', '')
    return t


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
                        if question_name == 'Alter':
                            print(question_name)
                        if question_name in params[template_name][group_name]:
                            answer_name = question.attrib['Answer']
                            template_dict.update({f'{template_name}//{group_name}::{question_name}': answer_name})
            d = d.append(template_dict, ignore_index=True)
        except KeyError:
            template_name = template.attrib['Header']
            print(f'ERROR::KeyError with key {template_name}')
        # d = d.append(template_dict, ignore_index=True)
    return d


def main(input_file='./01_Data/20211104_Mint_Export.xml',
         required_parameters='./01_Data/required_parameters.json',
         anonymization='UUID4'):
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
        data, info = main(input_file=xml_files[0], required_parameters=required_parameters, **args)

        print('INFO::Save excel file')
        out_file = os.path.join(script_dir, f'{info}_raw_data_risk-model.xlsx', )
        data.to_excel(out_file, index=False)

        print('DONE::XML extraction finished')

        stop = datetime.now()
        print(f'INFO::Total operation time: {stop - start}')
    else:
        print('INFO::No XML files found in this directory. Stop processing.')
    input('TODO::Press enter to close this window.')
