import pandas as pd

# Import des librairies
import pandas as pd
import locale
import datetime
import numpy as np
from datetime import timedelta


year_etude = 2022
date_max = pd.to_datetime(datetime.date(year_etude, 12, 31))
date_min = pd.to_datetime(datetime.date(year_etude - 10, 12, 31))
date_don = "date_don" # Date du don
num_client = "Num_Donateur" # Numéro client qui permet de faire les jointures

base_spf = pd.read_csv("Table_dons_202304_final_delai.csv", 
                    header = 0,
                    encoding='UTF-8',
                    sep=';',
                    parse_dates=["date_don","date_premdon","date_prempa","date_prem_MD","date_prem_TEL","date_prem_WEB","date_prem_WEB_DP","stop_pa"],
                    low_memory=False)

base_spf = base_spf.sort_values(by=[num_client, date_don])
# On aggrège pour avoir les informations sur le premier don. Don web ? don DP ? 
don_aggregation = base_spf.groupby(by=num_client).agg(date_don_max = (date_don, 'max'), 
                                                                date_don_min = (date_don, 'min') ,
                                                                date_premdon = ("date_premdon", 'min'),
                                                                top_don_WEB_first = ("top_don_WEB", 'first'),
                                                                top_don_pa_first = ("top_don_pa", 'first'),
                                                                date_prem_WEB = ("date_prem_WEB","first"),
                                                                date_prempa = ("date_prempa", 'min'),
                                                                montant_first = ("montant","first"),
                                                                Delai_next = ("Delai","first"),
                                                                donateur_fede = ("top_don_fede","first"),
                                                                Code_media_first = ("Code_media","first")
                                                                ).reset_index()

def structure_base_donateurs(year, df, col_num_client, col_date_ref, 
                             col_top_don_PA, col_date_prem_don, col_date_prempa, col_stop_PA) :
    
    # Base 0-48 : Sélection des dons qui ont eu lieu au cours des 4 dernières années
    don_base_0_48 = df[(df[col_date_ref] >= datetime.datetime(year-3, 1, 1)) &
                                 (df[col_date_ref] <= datetime.datetime(year, 12, 31))]
    
    # Ordonner les données :  Don le plus ancien en premier
    don_base_0_48 = don_base_0_48.sort_values(by=[col_num_client, col_date_ref])
    
    # Aggregation par client sur la base 0-48 :don le plus ancien, don le plus récent, 
    # top_don_pa du premier don, date du premier don, date du premier PA
    
    don_aggregation_0_48 = don_base_0_48.groupby(by = col_num_client).agg(date_don_max = (col_date_ref, 'max'), 
                                                      date_don_min = (col_date_ref, 'min') ,
                                                      top_don_pa_first = (col_top_don_PA, 'first'),
                                                      date_prem_don = (col_date_prem_don, 'min')).reset_index()
    
    ############################
    #### Inactif 24-48 mois ####
    ############################
    
    # Donateur qui n'a pas fait de don depuis 24 mois (don max qui remonte à plus de 2 ans)
    Inactif_24_48 = don_aggregation_0_48[(don_aggregation_0_48.date_don_max >= datetime.datetime(year-3, 1, 1)) &
                          (don_aggregation_0_48.date_don_max <= datetime.datetime(year-2, 12, 31))][col_num_client].nunique()
    
    ###########################
    #### Actifs 12-24 mois ####
    ###########################
    
    # Donateur qui a fait un don il y a plus de 12 mois (entre 12 et 24 mois)
    Actif_12_24 = don_aggregation_0_48[(don_aggregation_0_48.date_don_max >= datetime.datetime(year-1, 1, 1)) & 
                        (don_aggregation_0_48.date_don_max <= datetime.datetime(year-1, 12, 31))][col_num_client].nunique()
    
    ##################################
    #### Recruté et transformé PA ####
    ##################################
    
    # Définition :  Premier prélèvement PA dans l'année + non stoppé dans l'année
    # Sélection des dons PA ou la date du premier prélèvement PA a lieu dans l'année + non stoppé ou stoppé après l'année spécifiée
    PA_actif_recrute = don_base_0_48[(don_base_0_48[col_top_don_PA] == 1) & 
                                          (don_base_0_48[col_date_prempa] >= datetime.datetime(year, 1, 1)) &
                                          (don_base_0_48[col_date_prempa] <= datetime.datetime(year, 12, 31)) &
                                          ((don_base_0_48[col_stop_PA].isnull()) | (don_base_0_48[col_stop_PA] > datetime.datetime(year, 12, 31)))]
    
    donateur_PA_actif_recrute = PA_actif_recrute[col_num_client].unique()
    recrute_transfo_PA = PA_actif_recrute[col_num_client].nunique()

    ##################
    #### PA actif ####
    ##################
    
    # Définition : Activité PA sur l'année courante et non stoppé dans l'année + ne fait pas partie des recrutés et transformés PA

    PA_actif = don_base_0_48[(don_base_0_48[col_top_don_PA] == 1) & 
                                      (don_base_0_48[col_date_ref] >= datetime.datetime(year, 1, 1)) &
                                      (don_base_0_48[col_date_ref] <= datetime.datetime(year, 12, 31)) &
                                      ((don_base_0_48[col_stop_PA].isnull()) |
                                      (don_base_0_48[col_stop_PA] > datetime.datetime(year, 12, 31))) ]
    PA_actif_all = PA_actif[col_num_client].unique()
    # ne fait pas partie des recrutés + transformés PA
    actifs_PA = len(np.setdiff1d(PA_actif_all, donateur_PA_actif_recrute))

    
    #####################
    #### Recrutés DP ####
    #####################
    
    # Définition : A réalisé son premier don dans l'année et démarré par un don DP + ne fait pas partie des recrutés transformés PA
    recrute_dp =  don_aggregation_0_48[(don_aggregation_0_48.date_prem_don >= datetime.datetime(year, 1, 1)) & 
                            (don_aggregation_0_48.date_prem_don <= datetime.datetime(year, 12, 31)) &
                            (don_aggregation_0_48.top_don_pa_first != 1) & # le premier don du donateur n'est pas un don PA don un don DP
                            (~don_aggregation_0_48[col_num_client].isin(PA_actif_all))] # ne fait pas partie des transfomés PA
    recrute_dp_0_12 = recrute_dp[col_num_client].nunique()
    
    #####################
    #### Actifs 0-12 ####
    #####################
    
    # Définition : A été actif en 2021 et ne fait pas partie des recrutés DP ni des actifs PA
    don_actif = don_aggregation_0_48[(don_aggregation_0_48.date_don_max >= datetime.datetime(year, 1, 1)) &
                                     (don_aggregation_0_48.date_don_max <= datetime.datetime(year, 12, 31)) &
                                     (~don_aggregation_0_48[col_num_client].isin(PA_actif_all)) &
                                     (~don_aggregation_0_48[col_num_client].isin(recrute_dp[col_num_client].unique()))]
    actif_0_12 = don_actif[col_num_client].nunique()
    
    
    
    ################################################
    ### Création du dataframe avec les résultats ###
    ################################################
    
    data = {'Catégories': ['PA Actifs', 'Recrutés + Transformés PA',
                           'Recrutés 0-12 mois', 'Actifs 0-12 mois',
                           'Actifs 12-24 mois', 'Inactifs 24-48 mois'],
        year: [actifs_PA, recrute_transfo_PA, recrute_dp_0_12, 
               actif_0_12, Actif_12_24, Inactif_24_48]}
 
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

year_A = structure_base_donateurs(year_etude, base_spf, num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")

year_A_1 = structure_base_donateurs(year_etude-1, base_spf, num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")

structure_base = pd.merge(year_A_1,year_A, on ="Catégories",how ="left")
structure_base.columns = ["Catégories", "2021", "2022"]

year_A_fede = structure_base_donateurs(year_etude, base_spf.loc[base_spf.top_don_fede == 1], num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")
year_A_nat = structure_base_donateurs(year_etude, base_spf.loc[base_spf.top_don_fede == 0], num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")

year_A_1_fede = structure_base_donateurs(year_etude-1, base_spf.loc[base_spf.top_don_fede == 1], num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")
year_A_1_nat = structure_base_donateurs(year_etude-1, base_spf.loc[base_spf.top_don_fede == 0], num_client, date_don, 
                         "top_don_pa", "date_premdon", "date_prempa","stop_pa")

structure_base_fede = pd.merge(year_A_1_fede,year_A_fede, on ="Catégories",how ="left")
structure_base_fede.columns = ["Catégories", "2021", "2022"]

structure_base_nat = pd.merge(year_A_1_nat,year_A_nat, on ="Catégories",how ="left")
structure_base_nat.columns = ["Catégories", "2021", "2022"]

def flux_donateur_0_24(df, df_agg, year_etude,col_date_don, col_num_client) :
    
    # Construction de la base 0-24 en A et en A-1
    don_A = df[(df[date_don] >= datetime.datetime(year_etude -1,1,1)) & 
                       (df[date_don] <= datetime.datetime(year_etude,12,31))]
    don_A_1 = df[(df[date_don] >= datetime.datetime(year_etude-2,1,1)) &
                         (df[date_don] <= datetime.datetime(year_etude-1,12,31))]
    
    # Recrutement DP : premier don dans l'année + premier don non PA
    recrute_dp_year =  df_agg[(df_agg.date_premdon.dt.year == year_etude) & (df_agg.top_don_pa_first == 0 )]

    # Recrutement PA : premier don dans l'année et c'est un don PA
    recrute_pa_year =  df_agg[(df_agg.date_premdon.dt.year == year_etude)  & (df_agg.top_don_pa_first == 1)]
    
    # Réactivé en 2021: Date de premier don avant l'année spécifiée, existante d'un don dans l'année
    # Donateur actif en 2021 avec son premier don de 2021 qui a un écart de plus de deux ans avec le précédent.
    # Si il n'y a pas de dons avant 2021 dans l'historique mais que la date du premier don est avant l'historique on regarde l'écart entre cette date et la date de référence
    donateur_reactive_year = df[(df.date_premdon.dt.year < year_etude) &
                 (df[col_date_don].dt.year == year_etude) &
                 ((df.Delai >= 365*2) | 
                  ((df.Delai.isnull()) & 
                   (pd.to_timedelta(df[col_date_don] - df.date_premdon).dt.days >= 365*2)))
    ][num_client].unique()
    
    # Mise en forme des résultats dans un dataframe
    recrute_pa = recrute_pa_year[num_client].nunique()
    recrute_dp = recrute_dp_year[num_client].nunique()
    reactive = len(donateur_reactive_year)
    hors_recrute_reactive = don_A[num_client].nunique() - (len(donateur_reactive_year)+recrute_dp_year[num_client].nunique()+recrute_pa_year[num_client].nunique())
    total_A = don_A[num_client].nunique()
    total_A_1 = don_A_1[num_client].nunique()
    data_A = {'Catégories': ['Recrutés PA', 'Recrutés DP',
                           'Réactivés', 'Hors recrutés et réactivés', 'Total'],
        year_etude : [recrute_pa, recrute_dp, reactive, 
               hors_recrute_reactive, total_A]}

    df_A = pd.DataFrame(data_A)

    data_A_1 = {'Catégories': ['Total','Hors recrutés et réactivés'],
        year_etude - 1 : [total_A_1, total_A_1]}
    df_A_1 = pd.DataFrame(data_A_1)

    flux_donateur = pd.merge(df_A_1, df_A, on = "Catégories", how ="right")
    
    
    #################### Age ############################
    
    # don_A_age = don_A[[num_client,"age"]].drop_duplicates().age.mean()
    # print("Moyenne âge  base 0-24 : ", don_A_age)
    
    # don_age_actif_dp = don_A[don_A.top_don_pa == 0][[num_client,"age"]].drop_duplicates().age.mean()
    # print("Moyenne âge Actif DP : ", don_age_actif_dp)

    # df_age = pd.DataFrame({"Âge moyen base 0-24" : [don_A_age], "Âge moyen actifs DP" : [don_age_actif_dp]})
    
    # return flux_donateur, df_age

    return flux_donateur

flux_donateur = flux_donateur_0_24(base_spf, don_aggregation, year_etude, date_don, num_client)

don_aggregation_fede = base_spf.loc[base_spf["top_don_fede"]==1].groupby(by=num_client).agg(date_don_max = (date_don, 'max'), 
                                                                date_don_min = (date_don, 'min') ,
                                                                date_premdon = ("date_premdon", 'min'),
                                                                top_don_WEB_first = ("top_don_WEB", 'first'),
                                                                top_don_pa_first = ("top_don_pa", 'first'),
                                                                date_prem_WEB_first = ("date_prem_WEB","first"),
                                                                date_prempa_first = ("date_prempa", 'min'),
                                                                montant_first = ("montant","first")).reset_index()

don_aggregation_nat = base_spf.loc[base_spf["top_don_fede"]==0].groupby(by=num_client).agg(date_don_max = (date_don, 'max'), 
                                                                date_don_min = (date_don, 'min') ,
                                                                date_premdon = ("date_premdon", 'min'),
                                                                top_don_WEB_first = ("top_don_WEB", 'first'),
                                                                top_don_pa_first = ("top_don_pa", 'first'),
                                                                date_prem_WEB_first = ("date_prem_WEB","first"),
                                                                date_prempa_first = ("date_prempa", 'min'),
                                                                montant_first = ("montant","first")).reset_index()

flux_donateur_nat = flux_donateur_0_24(base_spf.loc[base_spf["top_don_fede"]==0], don_aggregation_nat, year_etude, date_don, num_client)
flux_donateur_fede = flux_donateur_0_24(base_spf.loc[base_spf["top_don_fede"]==1], don_aggregation_fede, year_etude, date_don, num_client)


def flux_donateur_0_12_PA(df, num_client, year_etude) : 
    
    data_PA = {'Catégories': ['Actifs PA', 'Transformés PA',
                       'Recrutés PA'],
    year_etude : []}

    # Actif PA (au moins 1 don PA dans l'année) + stop PA après l'année écoulée ou nulle
    for year in range(year_etude-1,year_etude+1) :
        actif_pa = df[(df.Annee_don == year) &
                (df.top_don_pa == 1) &
                ((df.stop_pa > datetime.datetime(year+1,1,1)) | (df.stop_pa.isnull()) )][num_client].nunique()
        if year == year_etude :
            data_PA[year_etude].append(actif_pa)
            
        if year == year_etude -1 :
            data_A_1_PA = {'Catégories': ['Actifs PA'], year_etude-1 : [actif_pa]}
            df_PA_A_1 = pd.DataFrame(data_A_1_PA)

        print("Actif_PA en {} : {}".format(year,actif_pa))

    # Transforme PA : Premier PA dans l'année (pas le premier don) + stop PA après l'année écoulée ou nulle
    for year in range(year_etude-1,year_etude+1) :
        transforme_pa = df[(df.Annee_don == year) &
                            (df.date_prempa >= datetime.datetime(year, 1, 1)) &
                           (df.date_prempa <= datetime.datetime(year, 12, 31)) &
                               (df.date_prempa > df.date_premdon) &
                (df.top_don_pa == 1) &
                ((df.stop_pa > datetime.datetime(year+1,1,1)) | (df.stop_pa.isnull()) )][num_client].nunique()
        if year == year_etude :
            data_PA[year_etude].append(transforme_pa)
            

        print("transforme_PA : ", year,transforme_pa)

    # Recruté PA : le premier don est le premier don PA
    for year in range(year_etude-1,year_etude+1) :
        recrute_pa = df[(df.Annee_don == year) &
                            (df.date_prempa >= datetime.datetime(year, 1, 1)) &
                                (df.date_prempa == df.date_premdon) &
                                          (df.date_prempa <= datetime.datetime(year, 12, 31)) &
                (df.top_don_pa == 1) &
                ((df.stop_pa > datetime.datetime(year+1,1,1)) | (df.stop_pa.isnull()) )][num_client].nunique()
        if year == year_etude :
            data_PA[year_etude].append(recrute_pa)
            
        print("recrute_PA : ", year,recrute_pa)

    df_PA_A = pd.DataFrame(data_PA)
    flux_donateur_PA = pd.merge(df_PA_A_1, df_PA_A, on = "Catégories", how = "right")
    
    return flux_donateur_PA

flux_donateur_PA = flux_donateur_0_12_PA(base_spf, num_client, year_etude)
# Exclure la ligne "Total" du DataFrame
flux_donateur_PA.at[0, 2022] = flux_donateur_PA.at[0, 2022] - (flux_donateur_PA.at[1, 2022] + flux_donateur_PA.at[2, 2022])
flux_donateur_PA = flux_donateur_PA.iloc[::-1].reset_index(drop=True)

def flux_donateurs_0_12_WEB(df, df_agg, num_client, date_don, year_etude) : 
    
    # Construction de la base 0-24 en A et en A-1
    don_A = df[(df[date_don] >= datetime.datetime(year_etude -1,1,1)) & 
                       (df[date_don] <= datetime.datetime(year_etude,12,31))]
    don_A_1 = df[(df[date_don] >= datetime.datetime(year_etude-2,1,1)) &
                         (df[date_don] <= datetime.datetime(year_etude-1,12,31))]
    
    # Nombre de Web DP actif en A-1(base 0-12)
    donateur_web_actif_year_A_1 = don_A_1[(don_A_1.top_don_WEB == 1) &
              (don_A_1.top_don_pa == 0) &
              (don_A_1[date_don].dt.year == year_etude-1)][num_client].unique()
    
    data_A_1_WEB = {'Catégories': ['Actifs WEB'], year_etude-1 : [len(donateur_web_actif_year_A_1)]}
    df_WEB_A_1 = pd.DataFrame(data_A_1_WEB)
    
    donateur_web_actif_A = don_A[(don_A.top_don_WEB == 1) &
                                        (don_A.top_don_pa == 0) & 
                                        (don_A[date_don].dt.year == year_etude)][num_client].unique()
    
    # Recrté WEB DP : Donateur qui a réalié son premier don en 2021 (Premier don = don WEB DP)
    recrute_web_dp_A = df_agg[(df_agg.date_premdon.dt.year == year_etude) &
                 (df_agg.top_don_WEB_first == 1) &
                 (df_agg.top_don_pa_first == 0)][num_client].unique()
    
    # Transforme WEB DP :  Donateur qui a réalisé son premier don WEB DP dans l'année (mais pas le premier don = transformé)
    transforme_web_dp_A = don_A[(don_A[date_don] == don_A.date_prem_WEB_DP) & 
     (don_A.date_prem_WEB_DP.dt.year == year_etude) &
     (~don_A[num_client].isin(recrute_web_dp_A))][num_client].unique()
    
    # On regarde les dons des donateurs actifs WEB en 2020 et leurs activité en 2021
    # Donateurs qui ont donné  WEB en 2020 mais pas de dons web en 2021
    # Etude de l'activité PA et DP (Hors WEB)
    dons_HWEB = don_A[(don_A[date_don].dt.year == year_etude) & 
     (don_A[num_client].isin(donateur_web_actif_year_A_1)) & 
     (~don_A[num_client].isin(donateur_web_actif_A))]

    donateur_hweb = dons_HWEB.groupby(num_client).agg({"top_don_WEB" : [lambda x: x.nunique(), "max"],
                                                       "top_don_pa" : [lambda x: x.nunique(), "max"]})
    
    
    
    actifs_web = len(donateur_web_actif_A)
    recrute_web = len(recrute_web_dp_A)
    transforme_web = len(transforme_web_dp_A)
    data_A_WEB = {'Catégories': ['Actifs WEB', 'Recrutés WEB',
                           'Transformés WEB'],
        year_etude : [actifs_web, recrute_web, transforme_web]}
 
    df_A_WEB = pd.DataFrame(data_A_WEB)


    flux_donateur_WEB = pd.merge(df_WEB_A_1, df_A_WEB, on = "Catégories", how = "right")

    
    return flux_donateur_WEB,  donateur_hweb

flux_donateur_WEB,  donateur_hweb = flux_donateurs_0_12_WEB(base_spf, don_aggregation, num_client, date_don, year_etude)
# Exclure la ligne "Total" du DataFrame
flux_donateur_WEB.at[0, 2022] = flux_donateur_WEB.at[0, 2022] - (flux_donateur_WEB.at[1, 2022] + flux_donateur_WEB.at[2, 2022])
flux_donateur_WEB = flux_donateur_WEB.iloc[::-1].reset_index(drop=True)

def evolution_donateur_0_24(df, num_client, date_don,year_etude) : 

    data_evolution = {"Année" : list(range(year_etude - 8, year_etude +1)), 'Actifs 0-24 dont PA': [], 'Actifs 0-24 hors PA': []}

    # Evolution de la base des actifs dont PA
    for year in range(year_etude - 8, year_etude +1) :
        # Sélection de la période de 24 mois
        don_periode = df[(df[date_don] >= datetime.datetime(year-1, 1, 1)) &
                                (df[date_don] <= datetime.datetime(year, 12, 31))]
        actif = don_periode[num_client].nunique() # Nombre de clients unique identfié sur la péridode
        data_evolution['Actifs 0-24 dont PA'].append(actif)

        don_periode_PA = don_periode[(don_periode.top_don_pa == 1)] # Sélection des dons PA
        don_periode_hors_pa = don_periode[(~don_periode[num_client].isin(don_periode_PA[num_client].unique()))] # On ne sélectionne pas les donateurs qui ont réalisé un don PA sur l'année

        actif_hors_pa = don_periode_hors_pa[num_client].nunique()
        data_evolution['Actifs 0-24 hors PA'].append(actif_hors_pa)

    return pd.DataFrame(data_evolution)

data_evolution = evolution_donateur_0_24(base_spf, num_client, date_don, year_etude)


def evolution_donateur_0_12(df, num_client, date_don,year_etude) : 

    data_evolution = {"Année" : list(range(year_etude - 8, year_etude +1)), 'Actifs 0-12 dont PA': [], 'Actifs 0-12 hors PA': []}

    # Evolution de la base des actifs dont PA
    for year in range(year_etude - 8, year_etude +1) :
        don_periode = df[(df[date_don] >= datetime.datetime(year, 1, 1)) &
                                   (df[date_don] <= datetime.datetime(year, 12, 31))]
        actif = don_periode[num_client].nunique()
        data_evolution['Actifs 0-12 dont PA'].append(actif)

        don_periode_PA = don_periode[(don_periode.top_don_pa == 1)]
        don_periode_hors_pa = don_periode[(~don_periode[num_client].isin(don_periode_PA[num_client].unique()))]

        actif_hors_pa = don_periode_hors_pa[num_client].nunique()
        data_evolution['Actifs 0-12 hors PA'].append(actif_hors_pa)

    return pd.DataFrame(data_evolution)

data_evolution_0_12 = evolution_donateur_0_12(base_spf, num_client, date_don, year_etude)
