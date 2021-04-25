"""
Created on Sun April 18 2021

@author: Antoine Mathieu Collin
@email: antoine.mathieu-collin@kuleuven.be
@article: This code is part of the article: "XXXX"

@description: Creates a simple API to query the EP-full text database using a list of publication numbers.
"""

import pandas as pd
import numpy as np
import glob


class ApiEpoFullText:
    
    # parameters
    REGEX = "*.txt"
    SEP = '\t'
    LIMIT_EP_NB = 3600000
    
    # from input
    patstat_data = pd.DataFrame()
    
    # fitted data
    pub_nbs = []
    pub_data = {}
    
    
    def __init__(self):
        pass
    
    
    def fit_patstat_data(self, path = '', patstat_data = pd.DataFrame()):
        """ Input a patstat table into the API, containing at least the columns: 'publn_nr' and'publn_nr_original' """
        self.path = path
        self.patstat_data = patstat_data
        self.get_pub_numbers()
        self.clean_publication_numbers()
        self.create_buckets()
        
        
    def query(self):
        """We loop over the buckets to retrieve the data"""

        # for each bucket, we look for the data in the corresponding input file
        list_df = []
        for i, bucket in enumerate(self.pub_data.keys()):
            print('Bucket {} out of {}'.format(i+1, len(self.pub_data.keys())))
            l = self.pub_data[bucket]
            list_df.append(self.get_df(l))

        result_df = pd.concat(list_df)
        self.full_text_data = result_df
        return self.full_text_data
    
    
    ## Methods below should not be called from the outside of the class
        

    def get_pub_numbers(self):
        """
        This function retrives from a given PATSTAT dataset the list of associated publication numbers:
        publication numbers can be found in the variable 'publn_nr' but also in the variable 
        'publn_nr_original' ('old' publication numbers). 

        This fonction therefore extracts the content of the two columns, appends them toghether and 
        return a list.
        """
        
        # define the columns where the publication numbers are stored
        first_col = 'publn_nr'
        second_col = 'publn_nr_original'
        df = self.patstat_data
        # retrieve the content of the first column ('new' publication numbers)
        list_pubs_numbers = (df[first_col].to_frame().reset_index()[first_col].unique().tolist())
        # retrieve the content of the second column ('old' publication numbers)
        list_pubs_old_numbers = (df[second_col].to_frame().reset_index()[second_col].unique().tolist())
        # append the two lists
        self.pub_nbs = list_pubs_numbers + list_pubs_old_numbers
                         

    def clean_publication_numbers(self):
        """
        Removes publication numbers which cannot be found in the EP full text database

        # the publication nr can appear in the EP-full_text data only of it:
        # it is a seven-digits nb
        # it does not contain letters
        # <= 3600000
        """
        self.pub_nbs = [e for e in self.pub_nbs \
                        if len(str(e))==7 \
                        if any(f.isalpha() for f in e)==False \
                        if '-' not in e \
                        if int(e) < self.LIMIT_EP_NB]
        
        
    def create_buckets(self):
        """We create buckets in order to retrieve the data associated to the publication
        numbers in chunks"""

        # we store the publication numbers in a dictionnary according
        buckets = list(np.sort(list(set([e[:2] for e in self.pub_nbs]))))

        pub_data = {}
        for bucket in buckets:
            pub_ids = [e for e in self.pub_nbs if e[:2] == bucket]
            pub_data.update({bucket: pub_ids})
            
        self.pub_data = pub_data
    
    
    def get_df(self, l):
        """Retrieve the Pandas dataframe associated to the hashed publication numbers list"""

        new_col_names = [
        'publication_authority', # will always have the value "EP"
        'publication_number', # a seven-digit number
        'publication_kind', # see https://www.epo.org/searching-for-patents/helpful-resources/first-time-here/definitions.html
        'publication_date', # in format YYYY-MM-DD
        'language_text_component', # de, en, fr; xx means unknown
        'text_type', # TITLE, ABSTR, DESCR, CLAIM, AMEND, ACSTM, SREPT, PDFEP
        'text' 
        # it contains, where appropriate, XML tags for better structure. 
        # You will find the DTD applicable to all parts of the publication at: 
        # http://docs.epoline.org/ebd/doc/ep-patent-document-v1-5.dtd
        ]

        # since the list is predefined, this returns only one element (without the [0])
        df_to_open_nb = str(list(set([(str(e)[:2]) for e in l]))[0])

        # looking for all corresponding files in the path folder
        file = glob.glob(self.path + df_to_open_nb + self.REGEX)[0]

        # print info
        print('Retrieving data from ', file)

        # opening the right file
        data_sample = pd.read_csv(file, sep = self.SEP)

        # renaming the columns
        data_sample.columns = new_col_names

        # filtering the dataset with the list of publication numbers
        condition = data_sample.publication_number.isin(l)
        return data_sample[condition]

