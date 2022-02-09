import json, hashlib, re, os, sys, uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

date_columns = ['CT//StudyDate',
                'Laborparameter//Laborparameter::Labordaten: Erhebungsdatum',
                'Klinisch-anamnestische Information//Klinische Symptome::Beginn der klinischen Symptome',
                'Laborparameter//Virologie::Datum des aktuellsten RT-PCR-Tests',
                'Laborparameter//Virologie::Datum des vorherigen RT-PCR-Tests'
                ]

comorbidities_base = 'Klinisch-anamnestische Information//Komorbiditäten aus Arztbrief'
comorbidities_org = f'{comorbidities_base}::Andere Komorbiditäten'
comorbidities_date = f'{comorbidities_base}::Datum'
comorbidities_study_type = f'{comorbidities_base}::Untersuchungstyp'
comorbidities_dia = f'{comorbidities_base}::Diastolischer Blutdruck'
comorbidities_new = [comorbidities_date, comorbidities_study_type, comorbidities_dia]


def extract_date(s, regex=r'\d{4}[.-]\d{1,2}[.-]\d{1,2}', str_pattern='%Y-%m-%d', return_string=False):
    # Return np.nan if no date is found (in order to handle this column subsequently)
    try:
        match = re.search(regex, s)
        # Handle date format '%d.%m.%Y' if '%Y-%m-%d' (or similar ones) cannot be found
        if match is None:
            match = re.search(r'\d{2}.\d{2}.\d{4}', s)
            if match is None:
                return np.nan
            else:
                date_str = match.group()
                return date_str if return_string else datetime.strptime(date_str, '%d.%m.%Y').date()
        date_str = match.group()
        # Replace separator between year, month and date with '-'
        date_str = date_str.replace('.', '-')
        # If month digits are larger than 12, then we assume date pattern to be '%Y-%d-%m' instead of '%Y-%m-%d'
        if int(date_str.split('-')[1]) > 12:
            return date_str if return_string else datetime.strptime(date_str, '%Y-%d-%m').date()
        else:
            return date_str if return_string else datetime.strptime(date_str, str_pattern).date()
    except TypeError:
        return np.nan
    except AttributeError:
        return np.nan
    except:
        return np.nan


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


def create_empty_dataframe(params, additional_columns=None):
    """ Create dataframe for collecting patient information.

    Args:
        params: Dictionary containing the names of the required parameters.

    Returns:
        pd.Dataframe: Empty dataframe for case information.

    """
    data_dict = {'PatientID': [], 'Template': []}
    if additional_columns is not None:
        for col in additional_columns:
            data_dict.update({col: []})
    for template in list(params):
        for group in params[template]:
            for question in params[template][group]:
                data_dict.update({f'{template}//{group}::{question}': []})
    return pd.DataFrame(data_dict)


def get_study_dates(r):
    study_dates_dict = {}
    for assessment in r.iter('Assessment'):
        assessment_id = assessment.attrib['AssessmentID']
        dcm_studies = list(assessment.iter('DicomStudy'))
        if len(dcm_studies) > 1:
            print(
                f'WARNING::There is more than one dicom study in assessment ID {assessment_id}')
            continue
        for dcm_study in dcm_studies:
            study_date = dcm_study.attrib['StudyDate']
            study_dates_dict.update({assessment_id: study_date})
    return pd.DataFrame(study_dates_dict.items(), columns=['CT//AssessmentID', 'CT//StudyDate'])


def remove_non_ct_patients(df):
    patients = df['PatientID'].unique().tolist()
    non_ct = [patient for patient in patients if len(df[(df['PatientID'] == patient) & (df['Template'] == 'CT')]) == 0]
    return df[~df['PatientID'].isin(non_ct)]


def extract_earliest_ct_dates(cts):
    earliest_ct_dates = {}
    for patient, dates in cts.items():
        if np.nan in dates:
            dates.remove(np.nan)

        if len(dates) > 0:
            converted_dates = [datetime.strptime(t, '%Y-%m-%d') for t in dates]
            earliest_date = min(converted_dates)
            earliest_ct_dates[patient] = earliest_date
        else:
            print(f'WARNING::There is no CT date extracted for any CT of patient {patient}')
    return earliest_ct_dates


def extract_n_days(df, patients_list):
    n_days = {}
    for patient in patients_list:
        patient_days = df[df['PatientID'] == patient][
            'Arztbrief/KIS Angaben//Arztbrief/KIS Angaben::Tage seit Aufnahme'].unique().tolist()
        if np.nan in patient_days:
            patient_days.remove(np.nan)
        # Assumption: If there is an empty string, we assume the number of days since admission to be 0
        patient_days = [int(d) if d != '' else 0 for d in patient_days]
        # In case there is an empty sequence of patient_days, i.e., there is no such number specified, we assume it to be 0
        if len(patient_days) > 0:
            n_days[patient] = min(patient_days)
        else:
            n_days[patient] = 0
    return n_days


def calculate_baseline_date(df):
    patients = df['PatientID'].unique().tolist()
    ct_dates = {patient: df[df['PatientID'] == patient]['CT//StudyDate'].unique().tolist() for patient in patients}

    # Extract earliest date from list of CT dates
    earliest_ct_dates = extract_earliest_ct_dates(ct_dates)

    # Get minimum number of days since admission for each patient
    n_days = extract_n_days(df, patients)

    # Calculate baseline date for each patient
    baselines = {patient: earliest_ct_dates[patient] - timedelta(days=n_days[patient]) for patient in patients}

    return baselines, pd.DataFrame(baselines.items(), columns=['PatientID', 'Baseline Date Calculated'])


def get_time_difference(baseline, reference):
    try:
        if isinstance(reference, float):
            return reference
        return (reference - baseline).days
    except TypeError:
        return reference


def replace_date(baseline_date, reference_value):
    if isinstance(reference_value, float):
        return reference_value
    reference_date = extract_date(reference_value)
    return get_time_difference(baseline_date, reference_date)


def update_date_columns(df):
    for col in date_columns:
        df[col] = df.apply(lambda row: replace_date(row['Baseline Date Calculated'], row[col]), axis=1)
    return df


def extract_study_type(txt):
    if isinstance(txt, float):
        return txt
    txt = txt.lower()
    study_types = []
    if 'base' in txt:
        study_types.append('Baseline')
    if 'ct' in txt:
        study_types.append('CT')
    if 'zwi' in txt:
        study_types.append('Zwischenwert')
    return ', '.join(study_types)


def extract_dia(s):
    try:
        if s == 'Nicht beantwortet':
            return s
        s_mod = s.lower()
        match = re.search(r'dia#\d{2,3}', s_mod)
        if match is not None:
            return match.group().replace('dia#', '')
        match = re.search(r'dia\d{2,3}', s_mod)
        if match is not None:
            return match.group().replace('dia', '')
        return np.nan
    except TypeError:
        return s
    except AttributeError:
        return s


def extract_comorbidities_freetxt(df):
    df[comorbidities_date] = df.apply(
        lambda row: get_time_difference(row['Baseline Date Calculated'], extract_date(row[comorbidities_org])), axis=1)
    df[comorbidities_study_type] = df.apply(lambda row: extract_study_type(row[comorbidities_org]), axis=1)
    df[comorbidities_dia] = df.apply(lambda row: extract_dia(row[comorbidities_org]), axis=1)

    # Update column order
    columns = df.columns.tolist()
    for col in comorbidities_new:
        columns.remove(col)
    rel_index = columns.index(comorbidities_org)
    new_col_order = columns[:rel_index] + comorbidities_new + columns[(rel_index + 1):]

    return df[new_col_order]


def faulty_logs(df):
    with open('extraction_info.txt', 'w') as f:
        f.write(
            'In diesem Dokument werden alle Patienten IDs aufgeführt, welche auffällige Werte in den verschiedenen Datumsfeldern haben.\nAuffällig sind hier insbesondere Werte, welche einen Abstand von über 90 Tagen zum berechneten Baseline-Datum aufweisen.\nBitte überprüfen Sie diese IDs auf Richtigkeit und führen Sie den Parser anschließend ggf. erneut aus.')
        f.write(
            '\n\nWICHTIG: Bitte teilen Sie dieses Dokument NICHT mit uns oder anderen Standorten, da durch die IDs ansonsten personenbezogene Informationen geteilt werden.')
    faulty_dict = {}

    for col in date_columns:
        faulty_ids = set(df[df[col] > 90]['PatientID'])
        if len(faulty_ids) > 0:
            for id_ in faulty_ids:
                if id_ in faulty_dict:
                    faulty_dict[id_].append(col)
                else:
                    faulty_dict[id_] = [col]

    with open('extraction_info.txt', 'a') as f:
        for id_, columns in faulty_dict.items():
            f.write(f'\n\nID: {id_}')
            for col in columns:
                f.write(f'\n\t{col}')
            f.write('\n--------------------------------------------------------------------------------')

    return df


def anonymize(df, anonymization='UUID4'):
    if anonymization == 'UUID4':
        replacements = {id_: uuid.uuid4() for id_ in df['PatientID'].unique()}
    df['PatientID'] = df.apply(lambda row: replacements[row['PatientID']], axis=1)
    return df


def get_template_information(d, c, params):
    """ Extract all template information for a given case.

    Args:
        d: Dataframe containing information about previous cases.
        c: Current case (XML element)
        params: Dictionary containing the names of the required parameters.

    Returns:
        pd.DataFrame: Dataframe containing update case information

    """
    patient_id = c[0].attrib['PatientID']
    templates = list(c.iter('Task'))
    for j, template in enumerate(templates):
        try:
            template_name = clean_template_name(template.attrib['Header'])
            if template_name not in params.keys():
                continue
            template_dict = {'PatientID': patient_id, 'Template': template_name}
            if template_name == 'CT':
                template_dict.update({'CT//AssessmentID': template.attrib['AssessmentID']})
            for group in template.iter('Group'):
                group_name = group.attrib['Header']
                if group_name in params[template_name]:
                    for question in group.iter('Question'):
                        question_name = question.attrib['Question']
                        if question_name in params[template_name][group_name]:
                            answer_name = question.attrib['Answer']
                            template_dict.update({f'{template_name}//{group_name}::{question_name}': answer_name})
            d = d.append(template_dict, ignore_index=True)
        except KeyError:
            template_name = clean_template_name(template.attrib['Header'])
            print(f'ERROR::KeyError with key {template_name}')
    return d


def main(input_file,
         required_parameters,
         anonymization='UUID4',
         additional_columns=None):
    if isinstance(required_parameters, str):
        with open(required_parameters, encoding='utf-8') as json_file:
            required_parameters = json.load(json_file)

    print('INFO::Extracting tree and root objects from XML file')
    tree = et.parse(input_file)
    root = tree.getroot()

    all_cases = get_cases(root)
    n_cases = len(all_cases)

    data = create_empty_dataframe(params=required_parameters, additional_columns=additional_columns)

    print(f'INFO::Extracting case information')
    for i, case in enumerate(all_cases):
        if i % 100 == 0:  # Maybe 100 instead of 50
            print(f'INFO::Currently handling case: {i + 1}/{n_cases}')
        data = get_template_information(d=data, c=case, params=required_parameters)

    # Extract CT study dates
    print('INFO::Extract CT study dates from XML file')
    study_dates = get_study_dates(root)
    data = pd.merge(left=data, right=study_dates, on='CT//AssessmentID', how='left')

    # Remove patients without CT template
    data = remove_non_ct_patients(data)

    # Calculate baseline date for each patient
    print(f'INFO::Calculate baseline date for each patient')
    baselines, baseline_dates = calculate_baseline_date(data)
    data = pd.merge(left=data, right=baseline_dates, on='PatientID', how='left')
    data['Baseline Date Calculated'] = pd.to_datetime(data['Baseline Date Calculated']).apply(lambda x: x.date())

    # Update date columns relatively
    print(f'INFO::Update date columns to relative time difference to baseline date')
    data = update_date_columns(data)

    # Extract data from 3.20 freetext field
    print(f"INFO::Extract data from 'other comorbidities'")
    data = extract_comorbidities_freetxt(data)

    # Drop columns
    drop_columns = ['CT//AssessmentID', 'Baseline Date Calculated']
    data.drop(drop_columns, inplace=True, axis=1)

    # Move column CT//StudyDate
    ct_study_date = data.pop('CT//StudyDate')
    data.insert(loc=5, column='CT//StudyDate', value=ct_study_date)

    # Logging for faulty date columns
    data = faulty_logs(data)

    # Anonymize data
    data = anonymize(data)

    info = 'all'
    print("INFO::Data won't be filtered for certain patients")

    return data, info


if __name__ == '__main__':
    print('START::XML extraction started. This might take up to a few minutes...')

    args = {'anonymization': 'UUID4', 'additional_columns': ['CT//AssessmentID']}
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
        out_file = os.path.join(script_dir, f'{info}_raw_data_cov-rads-validation.xlsx')
        data.to_excel(out_file, index=False)

        print('DONE::XML extraction finished')

        stop = datetime.now()
        print(f'INFO::Total operation time: {stop - start}')
    else:
        print('INFO::No XML files found in this directory. Stop processing.')
    input('TODO::Press enter to close this window.')
