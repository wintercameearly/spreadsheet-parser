def store_daily_payments_data(current_file_path):
    try:
        data = pandas.read_excel(current_file_path, sheet_name=0, usecols='C:F')
        os.remove(current_file_path)
        data1 = data.dropna(axis=0, how='all', thresh=3)
        data2 = data1.dropna(axis=1, how='all')
        try:
            data2.columns = data2.iloc[0]
            if 'Description' in data2.columns:
                data2 = data2.iloc[1:, ].reindex()
            else:
                data2.columns = data2.iloc[1]
                data2 = data2.iloc[2:, ].reindex()
        except IndexError:
            continue

        data2.columns = data2.columns.str.lower()
        df = data2.rename(
            columns={'beneficiary name': 'project_recipient_name', 'amount': 'project_amount',
                     'description': 'project_description', 'organization name': 'organization_name'})

        name = f'{day}-{month}-{year}'
        date = datetime.strptime(name, '%d-%m-%Y').date()
        df['project_date'] = date
        valid_data = ['JAN', 'FEB', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        pattern = ' 20|'.join(valid_data)
        df['project_description'] = np.where(df['project_description'].str.contains(pattern, na=False),
                                             df['project_description'].str[10:],
                                             df['project_description'])
        df['MDA_name'] = 'FEDERAL GOVERNMENT'
        df['project_amount'] = df['project_amount'].apply(lambda x: '{:.2f}'.format(x))

        # store data in dict form. this is the data to loop over to store into db
        daily_expenses = df.to_dict(orient='records')
    except KeyError:
        continue

    # code to store into database...
    for transaction in daily_expenses:
        if not Budget.objects.filter(MDA_name=transaction['MDA_name'],
                                     project_recipient_name=transaction['project_recipient_name'],
                                     project_name=transaction['organization_name'],
                                     project_amount = transaction['project_amount'],
                                     project_date=transaction['project_date']
                                     ).exists():
            budget = Budget()
            budget.MDA_name = transaction['MDA_name']
            budget.project_recipient_name = transaction['project_recipient_name']
            budget.project_name = transaction['organization_name']
            budget.project_amount = transaction['project_amount']
            budget.project_date = transaction['project_date']
            budget.save()
    return Response(status=status.HTTP_200_OK)


def get_daily_data():
    #x = requests.get('https://parser.microapi.dev/daily')
    store_daily_payments_data('media/daily/27-06-20.xlsx')
