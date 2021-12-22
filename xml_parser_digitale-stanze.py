# %%
import xml.etree.ElementTree as et
import os
import pandas as pd
import hashlib
import string
import random
import argparse
import uuid


# parse cases as list
def getAllCases() -> list:
    cases = []
    for trial in root.iter('Trial'):
        for trialArm in trial.iter('TrialArm'):
            for case in trialArm.iter('Case'):
                cases.append(case)
    return cases

# parse reference measurement of air pre-sternal
def getpresternal(referenzmessung):
    stanze = []
    for lesion in referenzmessung:
        for genericMeasurements in lesion.iter('GenericMeasurement'):
            stanze.append(genericMeasurements)
    return stanze

# parse dicom tag information from which the lesion was measured
def get_dicom_info(lesion):
    dicom_information = {}

    for MeasurementRecord in lesion[1].iter('MeasurementRecord'):
        StudyDescription = MeasurementRecord.attrib['StudyDescription']
        SeriesDescription = MeasurementRecord.attrib['SeriesDescription']         
        SliceThickness = MeasurementRecord.attrib['SliceThickness']
        PixelSpacing = MeasurementRecord.attrib['PixelSpacing0']
        string2hash = MeasurementRecord.attrib['StudyUID'] + MeasurementRecord.attrib['StudyDate']
        StudyID = encrypt(string2hash)

        dicom_information = dict(StudyID = StudyID,
                        StudyDescription = StudyDescription,
                        SeriesDescription = SeriesDescription,
                        SliceThickness = SliceThickness,
                        PixelSpacing = PixelSpacing)
    return dicom_information

# takes the histogramm in the form of Bins, Frequency, Value to make a histogramm list.
def get_histogramm(lesion):
    histogram_attrib = {}
    histogram_data = []
    for Histogram in lesion[1].iter('Histogram'):
    #print (Histogram.attrib)
        histogram_attrib = Histogram.attrib
        #histogram_data = []
        for bin in Histogram.iter('Bin'):
            for i in range(int(bin.attrib['Frequency'])):
                histogram_data.append(float(bin.attrib['Value']))
    return histogram_data, histogram_attrib 

# parse information regarding covid assessment
def get_covid_assessment(case):
    covid_assessment = {}
    label_list = ["COV-RADS Klassifikation*","COVID-19 CT-morphologische Klassifikation", "CO-RADS Klassifikation", "Ausdehnung der Pneumonie"]

    for Question in case.iter('Question'):
        try:
            question_label = Question.attrib['Question']
            if question_label == "Klassifikation des Lungenbefalls":
                answer = Question.attrib['Answer']
                covid_assessment[question_label] = answer
        except:
            question_label = ""
            answer = ""

        try:
            question_label = Question.attrib['Label']
            if question_label in label_list:
                answer = Question.attrib['Answer']
                covid_assessment[question_label] = answer
        except:
            question_label = ""
            answer = ""

        try:
            question_label = Question.attrib['Text']
            if question_label == "Nativ":
                answer = Question.attrib['Answer']
                covid_assessment[question_label] = answer
        except:
            question_label = ""
            answer = ""
            
    return covid_assessment

# change to sha256 hash for anonymisation

def encrypt(string):
    hash_object = hashlib.sha256(string.encode())
    hash_string = hash_object.hexdigest()
    return hash_string

def get_random_characters():
    random_source = string.ascii_letters + string.digits + string.punctuation
    characters = random.choice(string.ascii_lowercase)
    characters += random.choice(string.ascii_uppercase)
    characters += random.choice(string.digits)
    characters += random.choice(string.punctuation)
    for i in range(6):
        characters += random.choice(random_source)

    characters_list = list(characters)
    # shuffle all characters
    random.SystemRandom().shuffle(characters_list)
    characters = ''.join(characters_list)
    return characters

# sorry for the mess and ifs
def getCaseLesions(case, testing= False):
    lesion_list = []
    lesion_class = ''
    
    # case_string should be unique for each case and is used as anonymized patient_id with md5 hash
    case_string = case.attrib['CaseID'] + case[0].attrib['LastName'] + case[0].attrib['PatientID'] + case[0].attrib['InstitutionName']
    hash_string = encrypt(case_string)
    try:
        DaysSinceBaseline = case[1][1].attrib['DaysSinceBaseline']
    except:
        DaysSinceBaseline = ''

    covid_assessment = get_covid_assessment(case)

    for lesion in case.iter('Lesion'):
        Category = lesion.attrib['Category']
        LesionID = lesion.attrib['LesionID']
        if testing == True:
            print (LesionID)
        Organ = lesion.attrib['Organ']
        lesion_class = ''

        dicom_info = get_dicom_info(lesion)
        if Category == "Referenzmessungen" or "Lungenveränderungen":
            if Category == "Referenzmessungen":
                lesion_class = "Referenzmessung Lunge"
                if testing == True:
                    print (lesion_class)

            for question in lesion.iter('Question'):
                if question.attrib['Label'] == "Klassifikation der Pathologie" and question.attrib['Assessed'] == "true":
                    lesion_class = question.attrib['Answer']
                    if testing == True:
                        print (lesion_class)

            histogram_data, histogram_attrib = get_histogramm(lesion)

            case_lesion = dict(PatientID = hash_string,
                                Category = Category,
                                Lesion_class = lesion_class,
                                LesionID = LesionID,
                                Organ = Organ,
                                DaysSinceBaseline = DaysSinceBaseline
                                )
            case_lesion.update(dicom_info)
            case_lesion.update(covid_assessment)
            case_lesion.update(histogram_attrib)
            case_lesion['histogram'] = histogram_data
            lesion_list.append(case_lesion)

        # run almost same script on child tree for presternal reference value

            if Category == "Referenzmessungen":
                referenzmessung_presternal = lesion[2]
                lesion_class = lesion[2].attrib['Label']
                if testing == True:
                    print (lesion_class)

                dicom_info = get_dicom_info(referenzmessung_presternal)
                histogram_data, histogram_attrib = get_histogramm(referenzmessung_presternal)
                case_lesion = dict(PatientID = hash_string,
                                Category = Category,
                                Lesion_class = lesion_class,
                                LesionID = LesionID,
                                Organ = "Luft prästernale Höhe",
                                DaysSinceBaseline = DaysSinceBaseline
                                )
                
                case_lesion.update(dicom_info)
                case_lesion.update(covid_assessment)
                case_lesion.update(histogram_attrib)
                case_lesion['histogram'] = histogram_data
                lesion_list.append(case_lesion)
    return lesion_list

def randomize_patient_ids(lesion_list) :
    # convert patient ids to random uids which are disposed
    patient_ids = set([x['PatientID'] for x in lesion_list])
    random_uids = {}

    for patient_id in patient_ids :
        random_uids[patient_id] = uuid.uuid4()

    for i in range(len(lesion_list)):
        lesion_list[i]['PatientID'] = random_uids[lesion_list[i]['PatientID']]
    
    return lesion_list

# %%

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--random_ids', help='Uses random, disposed uids for patients', action='store_true')
    args = parser.parse_args()

    # process first xml file found in the script folder
    xml_file = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # for windows compiler use this

    print(script_dir)
    for file in os.listdir(script_dir):
        if ".xml" in file:
            xml_file.append(file)

    input_file = os.path.join(script_dir, xml_file[0])
    out_file = os.path.join(script_dir, 'lesion_histogram_list2.xlsx')
    print (f"processing {xml_file[0]}")
    print ('this may take some time - grab yourself a coffee!')
    tree = et.parse(input_file)
    root = tree.getroot()
    cases = getAllCases()

    lesion_list = []
    exception_list = []

    for case in cases:
        try:
            case_lesions = getCaseLesions(case)
            lesion_list.extend(case_lesions)
        except Exception as e:
            exception_list.append(e)

    if (args.random_ids) :
        lesion_list = randomize_patient_ids(lesion_list)

    df = pd.DataFrame.from_records(lesion_list)
    df.to_excel(out_file)
    print (f'{out_file} written successfully')

# %%
