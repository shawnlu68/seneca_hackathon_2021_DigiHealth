from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import pandas as pd
import numpy as np
import datetime

begin_time = datetime.datetime.now()

df = pd.read_csv('disorder_data_phenotypes.csv')

disorder_list = pd.unique(df['Disorder Name']).tolist()
hpo_list = pd.unique(df['HPO Term']).tolist()
hpo_list.sort()

freq_weight_conditions = [
    df['HPO Frequency'] == 'Excluded (0%)',
    df['HPO Frequency'] == 'Very rare (<4-1%)',
    df['HPO Frequency'] == 'Occasional (29-5%)',
    df['HPO Frequency'] == 'Frequent (79-30%)',
    df['HPO Frequency'] == 'Very frequent (99-80%)',
    df['HPO Frequency'] == 'Obligate (100%)',
]

freq_weight_choices = [
    0,
    0.2,
    0.4,
    0.6,
    0.8,
    1
]

df['weight'] = np.select(freq_weight_conditions, freq_weight_choices, default='N/A')
df['weight'] = df['weight'].astype(float)
d = df['weight'].sum()

df['hpo_appr'] = df['weight'].groupby(df['HPO Term']).transform('sum')
df['hpo_appr'] = df['hpo_appr'].astype(float)

df['idf'] = np.log10(d / (1 + df['hpo_appr']))
df['tf'] = df['weight'] / df['hpo_appr']
df['tfidf'] = df['tf'] * df['idf']


def tfidf_list(all_hpo):
    """
    takes a list of hpo terms and perform tfidf calculation on each of them
    stores the result in a dictionary in form of
    {disease: total tfidf score of the disease based on all given phenotype}
    """

    df['Result_relevance'] = np.where(
        df['HPO Term'].isin(all_hpo),
        df['tfidf'],
        np.nan
    )


def select_hpo(e):
    """append the double clicked phenotype to the PATIENT PHENOTYPE LIST box"""
    content = hpo_options.get(hpo_options.curselection())
    hpo_selected.insert(END, content)


def remove_hpo(e):
    """remove the double clicked phenotype from the PATIENT PHENOTYPE LIST box"""
    if hpo_selected.curselection():
        deletion = hpo_selected.curselection()
        hpo_selected.delete(deletion)
    else:
        pass


patient_hpo = []


def confirm_hpo():
    """
    finalize selection from the PATIENT PHENOTYPE LIST box
    and calculate the possibility of potential diseases;
    append all potential diseases to the Most Potential Disorders box
    with possibility in descending order (possibility hidden)
    """
    global patient_hpo
    patient_hpo = []
    patient_hpo.extend(list((hpo_selected.get(0, tkinter.END))))
    tfidf_list(patient_hpo)
    for index, row in df['Result_relevance'].groupby(df['Disorder Name'], sort=False,
                          dropna=True).sum().sort_values(ascending=False).reset_index().iterrows():
        if row ['Result_relevance'] != 0:
            patient_result.insert(END, row['Disorder Name'])
        else:
            pass
    df['Result_relevance'].fillna(0)
    print(datetime.datetime.now() - begin_time)

# beginning of GUI design phase
root = Tk()
root.title('Phenotype-based Disorder Searcher')
root.geometry('1440x720')

frm_label2 = Frame(root)
frm_label2.pack(side=TOP, fill=X)

frm_lb = Frame(root)
frm_lb.pack(side=TOP, fill=X)

frm_calc = Frame(root)
frm_calc.pack(side=BOTTOM)

Label(frm_label2, text='        LIST OF ALL PHENOTYPES  '
                       '(double click to add a phenotype to the '
                       'PATIENT PHENOTYPE LIST)').pack(side=LEFT)
Label(frm_label2, text='PATIENT PHENOTYPE LIST  '
                       '(double click to remove a selected phenotype)        '
                       '').pack(side=RIGHT)
Label(frm_lb, text='Press "Confirm Phenotypes" '
                   'when you finish selecting\n').pack(side=BOTTOM)

Label(frm_calc, text='Most Potential Disorders: '
                     '(Descending in possibility)').pack(side=TOP)

scrollbar = Scrollbar(frm_lb, orient='vertical')
scrollbar.pack(side=LEFT, fill=Y)
hpo_options = Listbox(frm_lb, width=100, height=20, yscrollcommand=scrollbar.set)
scrollbar.config(command=hpo_options.yview)

hpo_options.bind('<Double-Button-1>', select_hpo)
for hpo in hpo_list:
    hpo_options.insert(END, hpo)

hpo_selected = Listbox(frm_lb, width=100, height=20)
hpo_selected.bind('<Double-Button-1>', remove_hpo)

button_calc = Button(frm_lb, text='Confirm Phenotypes', command=confirm_hpo)
button_calc.pack(side=BOTTOM)

patient_result = Listbox(frm_calc, width=100, height=10)
patient_result.pack(side=BOTTOM)

hpo_options.pack(side=LEFT, fill=X)
hpo_selected.pack(side=LEFT, fill=X)
patient_result.pack(side=BOTTOM)

root.mainloop()
