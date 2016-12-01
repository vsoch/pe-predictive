## About PEFinder
PEFinder was [published by Chapman](chapman_pefinder.pdf) et. al, and credit for the knowledge base and model goes to this work. The original data and labels are not included in this application. This section will outline some of the details of the model.

### Training and Testing Labels
The original training and testing labels, for the model referenced in this paper from Pittsburgh, were the following:


      data['disease_state'].unique()
      Out[22]: array(['Neg', 'Pos', 'NULL'], dtype=object)

      In [23]: data['uncertainty'].unique()
      Out[23]: array(['No', 'Yes', 'NULL'], dtype=object)

      In [24]: data['quality'].unique()
      Out[24]: array(['Diagnostic', 'Not Diagnostic', 'NULL'], dtype=object)

      In [25]: data['historicity'].unique()
      Out[25]: array([None, 'New', 'Old', 'No Consensus', 'Mixed'], dtype=object)


### Knowledge Base
The [kb](../data/kb.pkl) object contains the knowledge base used to do the classification, which has the following fields:

#### Schema


      {1: ('AMBIVALENT', 'DISEASE_STATE == 2'),

       2: ('Negative/Certain/Acute', 'DISEASE_STATE == 0 and CERTAINTY_STATE == 1'),

       3: ('Negative/Uncertain/Chronic',
            'DISEASE_STATE == 0 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0'),

       4: ('Positive/Uncertain/Chronic',
            'DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0'),

       5: ('Positive/Certain/Chronic',
            'DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 0'),

       6: ('Negative/Uncertain/Acute',
            'DISEASE_STATE == 0 and CERTAINTY_STATE == 0'),

       7: ('Positive/Uncertain/Acute',
            'DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 1'),

       8: ('Positive/Certain/Acute',
            'DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 1')}


Schema is important as it shows the correspondence of PEFinder's classifications to sets of labels. For example, before any parsing, a raw result looks like this:

      {'pulmonary_embolism': (2, "\n<tagObject>\n<id> 138767256616807571703976633608436776968 </id>\n<phrase> PULMONARY EMBOLISM </phrase>\n<literal> pulmonary embolism </literal>\n<category> ['pulmonary_embolism'] </category>\n<spanStart> 3 </spanStart>\n<spanStop> 21 </spanStop>\n<scopeStart> 0 </scopeStart>\n<scopeStop> 22 </scopeStop>\n</tagObject>\n", [])}


Which is to say that for this case, the class given is `2` to signify that a classification of `Negative/Certain/Acute` was given, a `DISEASE_STATE` of 0 and `CERTAINTY_STATE` of 1.
