# seneca_hackathon_2021_DigiHealth

Put disorder_data_phenotypes.csv and the predictor_1_0.py file in the same folder, run the py file

In the new window, select from the left box the symptoms that the patient is showing by double clicking on symptom names,

remove symptoms by double clicking on symptom names in the right box.

When selection is done, press "Confirm Phenotypes", it might take a while since my code is not optimized at all, 

but eventually it gives you a list of possible diseases, in descending order with possibility.

The possibility is calculated with a method similar to the tf-idf method.


## summer 2021 vectorization update

Use predictor_1_1_vect.py instead of the old predictor_1_0.py

I have tried and used vectorization to improve run time, and it worked.

However, the code is far from clean, so please feel free to teach me anything, I really appreciate it.
