import csv

states = {
'Alabama' : 'AL',
'Alaska' : 'A',
'Arizona' : 'AZ',
'Arkansas' : 'AR',
'California' : 'CA',
'Colorado' : 'CO',
'Connecticut' : 'CT',
'Delaware' : 'DE',
'Florida' : 'FL',
'Georgia' : 'GA',
'Hawaii' : 'HI',
'Idaho' : 'ID',
'Illinois' : 'IL',
'Indiana' : 'IN',
'Iowa' : 'IA',
'Kansas' : 'KS',
'Kentucky' : 'KY',
'Louisiana' : 'LA',
'Maine' : 'ME',
'Maryland' : 'MD',
'Massachusetts' : 'MA',
'Michigan' : 'MI',
'Minnesota' : 'MN',
'Mississippi' : 'MS',
'Missouri' : 'MO',
'Montana' : 'MT',
'Nebraska' : 'NE',
'Nevada' : 'NV',
'New Hampshire' : 'NH',
'New Jersey' : 'NJ',
'New Mexico' : 'NM',
'New York' : 'NY',
'North Carolina' : 'NC',
'North Dakota' : 'ND',
'Ohio' : 'OH',
'Oklahoma' : 'OK',
'Oregon' : 'OR',
'Pennsylvania' : 'PA',
'Rhode Island' : 'RI',
'South Carolina' : 'SC',
'South Dakota' : 'SD',
'Tennessee' : 'TN',
'Texas' : 'TX',
'Utah' : 'UT',
'Vermont' : 'VT',
'Virginia' : 'VA',
'Washington' : 'WA',
'West Virginia' : 'WV',
'Wisconsin' : 'WI',
'Wyoming' : 'WY'
}

with open('dnac_map_template.csv') as map_file:
    reader = csv.DictReader(map_file) # list of dictionaries

    data = []
    list_of_states = []
    list_of_cities = []
    for line in reader:
        site = line['\ufeffGroupName']
        try:
            address = line['namespace:Location:address'].split(',')
            state = address[-1].strip()
            city = address[-2].strip()
            for key, value in states.items():
                if state == value:
                    state_full = key
            if state and city:


                # states
                if state not in list_of_states:
                    list_of_states.append(state)
                    data.append({'GroupName': state_full,
                                 'ParentHierarchy': 'Global',
                                 'GroupTypes': 'SITE',
                                 'namespace:Location:type': 'area',
                                 'namespace:Location:country': '',
                                 'namespace:Location:address': ''})

                # cities
                if f'{state}/{city}' not in list_of_cities:
                    list_of_cities.append(f'{state}/{city}')
                    data.append({'GroupName': city,
                                 'ParentHierarchy': f'Global/{state_full}',
                                 'GroupTypes': 'SITE',
                                 'namespace:Location:type': 'area',
                                 'namespace:Location:country': '',
                                 'namespace:Location:address': ''})

                # buildings
                data.append({'GroupName': line['\ufeffGroupName'],
                             'ParentHierarchy': f'Global/{state_full}/{city}',
                             'GroupTypes': 'SITE',
                             'namespace:Location:type': 'building',
                             'namespace:Location:country': 'United States',
                             'namespace:Location:address': line['namespace:Location:address']})
            else:
                print(f"Not possible to procced {site}. Please enter manually. Address: {line['namespace:Location:address']}")
        except:
            print(f"Not possible to procced {site}. Please enter manually. Address: {line['namespace:Location:address']}")

    with open('dnac_network_hierarchy_v2.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()), quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for d in data:
            writer.writerow(d)
