import json


def main():
    brillant_days = get_brilliant_days()

    for day in brillant_days:
        date = day[0].replace('-', '.')
        count = day[1]
        print(f'{date}: {count}')

def get_brilliant_days():
    with open('insights.json', 'r') as f:
        insights = json.load(f)


    moves_by_classification = insights['movesByClassificationOverTime']

    brillant_days = []

    print(len(moves_by_classification))
    for day in moves_by_classification.keys():
        if 'brilliant' in moves_by_classification[day]:
            brillant_days.append((day, moves_by_classification[day]['brilliant']))

    return brillant_days

if __name__ == '__main__':
    main()