from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import pandas as pd
import math

df = pd.read_csv('disorder_data_phenotypes.csv')


disorder_list = pd.unique(df['Disorder Name']).tolist()

freq_table = {'Excluded (0%)': 0,
              'Very rare (<4-1%)': 0.2,
              'Occasional (29-5%)': 0.4,
              'Frequent (79-30%)': 0.6,
              'Very frequent (99-80%)': 0.8,
              'Obligate (100%)': 1}

total = {}


for index, row in df.iterrows():
    if row['Disorder Name'] not in total:
        total[row['Disorder Name']] = freq_table[row['HPO Frequency']]
    else:
        total[row['Disorder Name']] += freq_table[row['HPO Frequency']]

d = sum(total.values())

tfidf_src = {}


def tfidf(hpo_incidence):
    """
    calculates the tf-idf score of a single hpo term
    based on disorder_data_phenotypes.csv;
    store the results in the tfidf_src dictionary in the form of
    {phenotype: {disease: tf-idf score of the phenotype in this disease}}
    """
    global tfidf_src
    tfidf_src = {hpo_incidence: {}}

    hpo_appr = 0
    for ind, ro in df.iterrows():
        if ro['HPO Term'] == hpo_incidence:
            hpo_appr += freq_table[ro['HPO Frequency']]

    idf = math.log10(d/(1 + hpo_appr))

    for i, r in df.iterrows():
        if r['HPO Term'] == hpo_incidence:
            tf = freq_table[r['HPO Frequency']] / total[r['Disorder Name']]
            tfidf_src[hpo_incidence][r['Disorder Name']] = tf * idf


tfidf_result = {}


def tfidf_list(all_hpo):
    """
    takes a list of hpo terms and perform tfidf calculation on each of them
    stores the result in a dictionary in form of
    {disease: total tfidf score of the disease based on all given phenotype}
    """
    global tfidf_result
    tfidf_result = {}
    for hpo_incidence in all_hpo:
        tfidf(hpo_incidence)
        for disorder in tfidf_src[hpo_incidence]:
            if disorder not in tfidf_result:
                tfidf_result[disorder] = tfidf_src[hpo_incidence][disorder]
            else:
                tfidf_result[disorder] += tfidf_src[hpo_incidence][disorder]

    tfidf_result = dict(sorted(tfidf_result.items(),
                               key=lambda x: x[1], reverse=True))


# beginning of GUI design phase
hpo_list = pd.unique(df['HPO Term']).tolist()
hpo_list.sort()

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
    for record in tfidf_result.keys():
        patient_result.insert(END, record)


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
