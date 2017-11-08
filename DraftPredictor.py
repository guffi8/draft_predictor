import io
import csv
import operator
import subprocess

# path Files with data of players we wish to predict their draft pick
PLAYERS_CSV_FILE_TO_PREDICT = "2016-2017.csv"
PLAYERS_CSV_FILE_2011 = "2010-2011.csv"

# path Files with output of our R script, which contain the vector of the importance of each feature
FEATURES_WEIGHTS_FILE_CONF = 'Vectors/FeatureWeightsAll.txt'
FEATURES_WEIGHTS_FILE_GUARDS_CONF = 'Vectors/FeatureWeightsGuards.txt'
FEATURES_WEIGHTS_FILE_FORWARDS_CONF = 'Vectors/FeatureWeightsForwards.txt'
FEATURES_WEIGHTS_FILE_CENTERS_CONF = 'Vectors/FeatureWeightsCenters.txt'


# from conference name to the array that represent the conference,
#  so it will fit the R script - it's a categorical variable
def fromConfToCategoricalNumber(x):
    return {
        'ACC': [0, 0, 0, 0, 0, 0, 0, 0],
        'Pac-12': [1, 0, 0, 0, 0, 0, 0, 0],
        'SEC': [0, 1, 0, 0, 0, 0, 0, 0],
        'Big Ten': [0, 0, 1, 0, 0, 0, 0, 0],
        'Big 12': [0, 0, 0, 1, 0, 0, 0, 0],
        'Big East': [0, 0, 0, 0, 1, 0, 0, 0],
        'MWC': [0, 0, 0, 0, 0, 1, 0, 0],
        'AAC': [0, 0, 0, 0, 0, 0, 1, 0],
    }.get(x, [0, 0, 0, 0, 0, 0, 0, 1])

# turn a file's content into a vector of floats
def load_features_weights(feature_file):
    with open(feature_file) as f:
        content = f.readlines()
    content = [float(feature.strip()) for feature in content if feature]
    return content


# turn a csv file into a dictionary - in this case, retrieving the player's data
def retrieve_players_data(csv_filepath):
    with io.open(csv_filepath, encoding='utf8') as csvfile:
        players = [{k: v for k, v in row.items()}
                     for row in csv.DictReader(csvfile, skipinitialspace=True)]

        # return the list of players
        return players


# creates a vector from the stats of a player
def gen_feature_vector(player_entry):

    player_conf = fromConfToCategoricalNumber(player_entry['Conf'])

    # turns the year of the player into an array that will match the r script, it's a categorical variable
    if player_entry['Class'] == 'FR':
        player_class = [0,0, 0, 0]
    elif player_entry['Class'] == 'SO':
        player_class = [1, 0, 0, 0]
    elif player_entry['Class'] == 'JR':
        player_class = [0, 1, 0, 0]
    elif player_entry['Class'] == 'SR':
        player_class = [0, 0, 1, 0]
    else:
        player_class = [0, 0, 0, 1]

    v = [float(player_entry['ORB']), float(player_entry['DRB']),
            float(player_entry['AST']), float(player_entry['STL']), float(player_entry['BLK']), float(player_entry['TOV']),
            float(player_entry['PF']), float(player_entry['PTS']), float(player_entry['FTPER']),
            float(player_entry['FGPER']), float(player_entry['3PPER']), ]

    # extends the array with the suitable conference data and year data
    v.extend(player_conf)
    v.extend(player_class)

    return v


# calculating inner product between the vector of the player data and the output of our R script
def get_player_rank(player_vector, FEATURES_WEIGHTS):
    result = 0
    result += FEATURES_WEIGHTS[0]
    for i in range(len(player_vector)):
        result += player_vector[i] * FEATURES_WEIGHTS[i + 1]

    return result

# retrieving the output of our R script as a vector
FEATURES_WEIGHTS_GUARDS = load_features_weights(FEATURES_WEIGHTS_FILE_GUARDS_CONF)
FEATURES_WEIGHTS_FORWARDS = load_features_weights(FEATURES_WEIGHTS_FILE_FORWARDS_CONF)
FEATURES_WEIGHTS_CENTERS  =load_features_weights(FEATURES_WEIGHTS_FILE_CENTERS_CONF)
FEATURES_WEIGHTS_ALL =  load_features_weights(FEATURES_WEIGHTS_FILE_CONF)

# retrieving the data of 2016-2017 college basketball season we collected
players_data_predict = retrieve_players_data(PLAYERS_CSV_FILE_TO_PREDICT)

player_grade_dict = dict()

# for each player we calculate his grade -  depending of his position
# we calculate player's grade by (his grade according to his position + his grades according to all general players)
for player in players_data_predict:
    if player['Pos'] == 'G':
        featureWeightsPosConf = FEATURES_WEIGHTS_GUARDS
    elif player['Pos'] == 'F':
        featureWeightsPosConf = FEATURES_WEIGHTS_FORWARDS
    else:
        featureWeightsPosConf = FEATURES_WEIGHTS_CENTERS

    player_grade = get_player_rank(gen_feature_vector(player), FEATURES_WEIGHTS_ALL) + get_player_rank(gen_feature_vector(player), featureWeightsPosConf)
    player_grade_dict[player['Player']] = [player_grade, player['School'], player['Pos']]

# print top 11 players
final_predict_list = sorted(player_grade_dict.items(), key=operator.itemgetter(1), reverse=True)
print ("Top 11 Draft Predictions in Draft 2017:")
for counter, player_data in enumerate(final_predict_list[:11]):
    print (str(counter + 1) + ": " +str(player_data))
print ("----------------------------------------------------------------------------------")

# doing the same with 2010-2011 players
players_data_predict = retrieve_players_data(PLAYERS_CSV_FILE_2011)
player_grade_dict = dict()

# for each player we calculate his grade -  depending of his position
# we calculate player's grade by (his grade according to his position + his grades according to all general players)
for player in players_data_predict:
    if player['Pos'] == 'G':
        featureWeightsPosConf = FEATURES_WEIGHTS_GUARDS
    elif player['Pos'] == 'F':
        featureWeightsPosConf = FEATURES_WEIGHTS_FORWARDS
    else:
        featureWeightsPosConf = FEATURES_WEIGHTS_CENTERS

    player_grade = get_player_rank(gen_feature_vector(player), FEATURES_WEIGHTS_ALL) + get_player_rank(gen_feature_vector(player), featureWeightsPosConf)
    player_grade_dict[player['Player']] = [player_grade, player['School'], player['Pos']]

# print top 11 players
final_predict_list = sorted(player_grade_dict.items(), key=operator.itemgetter(1), reverse=True)
print ("Top 11 Draft Predictions in Draft 2011:")
for counter, player_data in enumerate(final_predict_list[:11]):
    print (str(counter + 1) + ": " +str(player_data))