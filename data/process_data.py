import sys
import numpy as np
from sqlalchemy import create_engine
import pandas as pd
import sqlite3
import os.path


def load_data(messages_filepath, categories_filepath):
    
    #load messages data from csv
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    # merge messages and categories dataset
    df = pd.merge(messages, categories, left_on='id', right_on='id', how='outer')
    return df


def clean_data(df):
    # clean categories column in df
    
    # create a dataframe of the 36 individual category columns
    categories = df["categories"].str.split(";", expand=True)
    
    # extract columns from the first row and assign them to categories df
    row = categories.iloc[0]
    category_column_names =  row.apply(lambda x: x[:-2])
    categories.columns = category_column_names
    
    for column in categories:
         categories[column] = categories[column].astype(str).str[-1]
         categories[column] =categories[column].astype(int)

    # drop the original categories column from `df`
    df.drop("categories", axis=1, inplace=True)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df =  pd.concat([df,categories], axis=1)
    
    df['related'] = df['related'].map({0:0,1:1,2:1})
    
    # drop duplicates
    df.drop_duplicates(inplace=True)
    
    return df


def save_data(df, database_filename): 
        
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('msg_Disa', engine, index=False , if_exists = 'replace') 

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()