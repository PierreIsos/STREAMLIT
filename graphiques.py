import pandas as pd
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties, findSystemFonts
import locale

def generate_graphs(structure_base,year):
    # Charger la police Montserrat
    montserrat_font = FontProperties(family='Montserrat', style='normal', weight='normal', size=12)

    # Calculer les totaux par catégorie pour chaque année
    structure_base['Total_2022'] = structure_base[year].sum()

    # Définir les couleurs précises
    colors = {
        'PA Actifs': '#FFC600',  # Citron
        'Recrutés + Transformés PA': '#FFE78F',  # Citron
        'Recrutés 0-12 mois': '#0069B4',  # Azur
        'Actifs 0-12 mois': '#0081E2',  # Azur
        'Actifs 12-24 mois': '#29A3FF',  # Azur
        'Inactifs 24-48 mois': '#DBDBDB'  # Gris
    }

    # Définir une palette de couleurs avec dégradé
    cmap = LinearSegmentedColormap.from_list('custom', [colors[key] for key in structure_base['Catégories']], N=len(structure_base['Catégories']))

    # Créer une figure
    fig, ax = plt.subplots(figsize=(8, 8))

    def custom_format(pct):
        value = int(pct * sum(structure_base[year]) / 100)
        return f'{value:,.0f}'.replace(',', ' ').replace('.', ',') + f'\n{pct:.0f}%'

    wedges, texts, autotexts = ax.pie(structure_base[year], labels=None, startangle=90,
                                      colors=[colors[key] for key in structure_base['Catégories']],
                                      autopct=custom_format,
                                      pctdistance=0.80, labeldistance=1.4,
                                      textprops=dict(horizontalalignment='center',
                                                      verticalalignment='center', fontproperties=montserrat_font), wedgeprops=dict(width=0.4, edgecolor='w'))

    # Mettre en noir le texte pour les deux premiers azur et le premier citron
    for i, autotext in enumerate(autotexts):
        if i < 2 or (structure_base['Catégories'][i] == 'PA Actifs' and i == 2):
            autotext.set_color('black')

    # Ajouter les valeurs exactes du DataFrame à l'intérieur des blocs
    for text, value in zip(autotexts, structure_base[year]):
        pct = text.get_text().split("\n")[1]
        text.set_text(f'{value:,.0f}'.replace(',', ' ').replace('.', ',') + f'\n{pct}')

    # Centrer les pourcentages et les valeurs dans chaque segment
    for autotext in autotexts:
        autotext.set_horizontalalignment('center')
        autotext.set_verticalalignment('center')

    # Ajouter le nom des catégories à côté de chaque section
    for i, (category, autotext) in enumerate(zip(structure_base['Catégories'], autotexts)):
        angle = (wedges[i].theta2 + wedges[i].theta1) / 2.
        x = wedges[i].r * 1.25 * np.cos(np.deg2rad(angle))
        y = wedges[i].r * 1.25 * np.sin(np.deg2rad(angle))
        ax.annotate(category, (x, y), xytext=(1.35*np.cos(angle), 1.35*np.sin(angle)),
                    horizontalalignment='center', verticalalignment='center',
                    textcoords='offset points')

    # Retourner la figure
    return fig

# Dans votre fichier graphiques.py

def generate_stacked_bar_chart(flux_donateur):
        # Exclure la ligne "Total" du DataFrame
        # Exclure la ligne "Total" du DataFrame
    flux_donateur2 = flux_donateur[flux_donateur["Catégories"] != "Total"]

    # Calculer la colonne de valeurs cumulatives pour "2022"
    cum_values = np.cumsum(np.flip(flux_donateur[2022].values[:-1]))

    # Transposer le DataFrame pour avoir les années en index
    flux_donateur2 = flux_donateur2.set_index("Catégories").T
    flux_donateur2 = flux_donateur2.iloc[:, ::-1]

    # Créer le graphique empilé
    ax = flux_donateur2.plot(kind='bar', stacked=True, figsize=(10, 6), 
                            edgecolor='none', color=['#0069B4', '#DBDBDB', '#338DCF', "#FFC600"])  # Supprimer les contours

    # Ajouter des étiquettes
    ax.set_xlabel('Année', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des abscisses
    ax.set_ylabel('Nombre', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des ordonnées

    # Mettre les années à l'horizontale
    plt.xticks(rotation=0)

    # Supprimer les bordures du graphique
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Supprimer l'échelle à gauche
    ax.get_yaxis().set_visible(False)

    # Définir la locale pour le formatage des chiffres
    locale.setlocale(locale.LC_NUMERIC, '')  # Utilise la locale par défaut du système

    # Ajouter la valeur au-dessus des histogrammes empilés (manuellement centré)
    col_i =-1
    for col in flux_donateur2.columns:
        col_i += 1
        for i, val in enumerate(flux_donateur2[col]):
            if val > 0 and i == 1:
                if col_i != 0:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[col_i -1] + cum_values[col_i])/2),
                                ha='center', va='center', fontsize=10, color='black',fontname='Montserrat')
                else:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[0])/2),
                                ha='center', va='center', fontsize=10, color='black',fontname='Montserrat')
            if val > 0 and i == 0:
                ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                            (i, (val)/2),
                            ha='center', va='center', fontsize=10, color='black',fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur[2021].values[4], grouping=True)}',
                            (0, flux_donateur[2021].values[4] + 5000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black',fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur[2022].values[4] , grouping=True)}',
                            (1, flux_donateur[2022].values[4] + 5000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black',fontname='Montserrat')

    # Supprimer la légende
    ax.legend().set_visible(False)
        
    # Retourner l'objet de la figure
    return ax.figure

def PA_chart(flux_donateur_PA):
    flux_donateur2 = flux_donateur_PA.copy()

    # Calculer la colonne de valeurs cumulatives pour "2023"
    cum_values = np.cumsum(np.flip(flux_donateur2[2022].values))

    # Transposer le DataFrame pour avoir les années en index
    flux_donateur2 = flux_donateur2.set_index("Catégories").T
    flux_donateur2 = flux_donateur2.iloc[:, ::-1]

    # Créer le graphique empilé
    ax = flux_donateur2.plot(kind='bar', stacked=True, figsize=(10, 6), 
                            edgecolor='none', color=['#FFC600', '#EA5B0C', '#FFE78F'])  # Supprimer les contours

    # Ajouter des étiquettes
    ax.set_xlabel('Année', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des abscisses
    ax.set_ylabel('Nombre', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des ordonnées

    # Mettre les années à l'horizontale
    plt.xticks(rotation=0)

    # Supprimer les bordures du graphique
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Supprimer l'échelle à gauche
    ax.get_yaxis().set_visible(False)

    # Définir la locale pour le formatage des chiffres
    locale.setlocale(locale.LC_NUMERIC, '')  # Utilise la locale par défaut du système

    # Ajouter la valeur au-dessus des histogrammes empilés (manuellement centré)
    col_i =-1
    for col in flux_donateur2.columns:
        col_i += 1
        for i, val in enumerate(flux_donateur2[col]):
            if val > 0 and i == 1:
                if col_i != 0:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[col_i -1] + cum_values[col_i])/2),
                                ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
                else:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[0])/2),
                                ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
            if val > 0 and i == 0:
                ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                            (i, (val)/2),
                            ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur_PA[2021].sum(), grouping=True)}',
                            (0, flux_donateur_PA[2021].sum() + 1000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black', fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur_PA[2022].sum() , grouping=True)}',
                            (1, flux_donateur_PA[2022].sum()+ 1000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black', fontname='Montserrat')

    # Supprimer la légende
    ax.legend().set_visible(False)

    # Retourner l'objet de la figure
    return ax.figure

def WEB_chart(flux_donateur_WEB):
    flux_donateur2 = flux_donateur_WEB.copy()

    # Calculer la colonne de valeurs cumulatives pour "2023"
    cum_values = np.cumsum(np.flip(flux_donateur2[2022].values))

    # Transposer le DataFrame pour avoir les années en index
    flux_donateur2 = flux_donateur2.set_index("Catégories").T
    flux_donateur2 = flux_donateur2.iloc[:, ::-1]

    # Créer le graphique empilé
    ax = flux_donateur2.plot(kind='bar', stacked=True, figsize=(10, 6), 
                            edgecolor='none', color=['#75C087', '#548235', '#E2F0D9'])  # Supprimer les contours

    # Ajouter des étiquettes
    ax.set_xlabel('Année', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des abscisses
    ax.set_ylabel('Nombre', fontname='Montserrat')  # Police Montserrat pour le label de l'axe des ordonnées

    # Mettre les années à l'horizontale
    plt.xticks(rotation=0)

    # Supprimer les bordures du graphique
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Supprimer l'échelle à gauche
    ax.get_yaxis().set_visible(False)

    # Définir la locale pour le formatage des chiffres
    locale.setlocale(locale.LC_NUMERIC, '')  # Utilise la locale par défaut du système

    # Ajouter la valeur au-dessus des histogrammes empilés (manuellement centré)
    col_i =-1
    for col in flux_donateur2.columns:
        col_i += 1
        for i, val in enumerate(flux_donateur2[col]):
            if val > 0 and i == 1:
                if col_i != 0:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[col_i -1] + cum_values[col_i])/2),
                                ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
                else:
                    ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                                (i, (cum_values[0])/2),
                                ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
            if val > 0 and i == 0:
                ax.annotate(f'{locale.format_string("%d", val, grouping=True)}',
                            (i, (val)/2),
                            ha='center', va='center', fontsize=10, color='black', fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur_WEB[2021].sum(), grouping=True)}',
                            (0, flux_donateur_WEB[2021].sum() + 1000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black', fontname='Montserrat')
    ax.annotate(f'{locale.format_string("%d",flux_donateur_WEB[2022].sum() , grouping=True)}',
                            (1, flux_donateur_WEB[2022].sum()+ 1000),
                            ha='center', va='center', fontweight='bold', fontsize=12, color='black', fontname='Montserrat')

    # Supprimer la légende
    ax.legend().set_visible(False)

    # Retourner l'objet de la figure
    return ax.figure

def Evol_donateurs(data_evolution):
        # Mappage des couleurs
    color_mapping = {
        'Actifs 0-24 dont PA' : '#0000FF',
        'Actifs 0-24 hors PA' : '#0071C4'}
    # Utiliser le dictionnaire pour créer la liste des couleurs dans le même ordre que les colonnes
    colors_ordered = [color_mapping[col] for col in ['Actifs 0-24 dont PA', 'Actifs 0-24 hors PA']]


    # Vérifier si la police 'Montserrat' est disponible, sinon utiliser une police par défaut
    montserrat_font = "sans-serif"
    for font in findSystemFonts():
        if "Montserrat" in font:
            montserrat_font = "Montserrat"
            break

    # Préparer les données pour le graphique
    x = data_evolution['Année']  # Les années seront sur l'axe des x
    y_columns = ['Actifs 0-24 dont PA', 'Actifs 0-24 hors PA']

    # Créer le graphique de courbes non empilées avec des marqueurs
    fig, ax = plt.subplots(figsize=(18, 12))  # Adjust these values as needed


    def add_annual_variation_labels_for_PA(ax, data, column_name):
        # Calculer les variations annuelles en pourcentage pour la colonne spécifiée
        annual_variations = data[column_name].pct_change().fillna(0)  # Utiliser fillna(0) pour gérer la première valeur NaN
        # print(annual_variations)  # Pour débogage

        for index, variation_pct in annual_variations.items():
            year = data.loc[index, 'Année']
            # print(f"Année : {year}, Variation : {variation_pct}")  # Pour débogage
            y_pos = data.loc[index, column_name]  # La position verticale est la valeur pour l'année
            if np.isfinite(year) and np.isfinite(y_pos):  # Vérifier si les positions sont finies
                # Déterminer la couleur de l'étiquette en fonction de la variation
                color = 'green' if variation_pct >= 0 else 'red'
                # Ajouter une étiquette de variation annuelle en pourcentage
                ax.text(year, y_pos + 0.18 * y_pos, f'{variation_pct:+.1%}', ha='center', va='bottom', fontsize=10,
                        color=color, fontname=montserrat_font, style='italic')  # Adjusting the position here



    texts = []  # Initialiser une liste pour stocker les objets de texte pour adjustText
    for i, col in enumerate(y_columns):
        values = data_evolution[col]
        color = color_mapping[col]  # Récupérer la couleur correspondante
        ax.plot(x, values, label=col, color=color, marker='o', linestyle='--', linewidth=1, markersize=6)

        for xi, yi in zip(x, values):
            value_label = f'{int(yi):,}'.replace(',', ' ')  # Format avec séparateur de milliers
            # Placer l'étiquette de valeur avec la couleur correspondante
            texts.append(ax.text(xi, yi - 10000, value_label, ha='center', va='bottom', fontsize=12, fontname=montserrat_font,
                                color=color, fontweight='bold'))
        

    # Ajustements additionnels
    # ax.set_title('Nombre de donateurs uniques par année et type de canal', fontsize=12, fontname=montserrat_font, loc="left")
    # ax.set_xlabel('Année', fontsize=12, fontname=montserrat_font)
    ax.set_xticks(x)  # Faire apparaître chaque année
    ax.set_xticklabels(ax.get_xticks(), fontweight='bold')

    ax.legend(loc='upper left', bbox_to_anchor=(0, 1.3), frameon=False, prop={'family': montserrat_font}) # Changez 1.15 pour ajuster la position verticale
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)  # Définir les bornes des ordonnées
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False, labelleft=False)  # Retirer les ticks de l'axe des ordonnées

    ax.grid(False)  # Rendre le quadrillage invisible
    ax.yaxis.set_visible(False)  # Cacher la colonne des ordonnées

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname(montserrat_font)

    # adjust_text(texts,
    #             avoid_text=True,  # Les étiquettes évitent de se chevaucher entre elles
    #             avoid_points=True,  # Les étiquettes évitent de se chevaucher avec les points
    #             expand_points=(1.5, 2)
    #             )

    # Ajouter les étiquettes de variation annuelle pour "Actifs 0-12 dont PA"
    add_annual_variation_labels_for_PA(ax, data_evolution, 'Actifs 0-24 dont PA')

    # Définir les limites de l'axe des ordonnées pour inclure zéro
    ax.set_ylim(0, 250000)

    return ax.figure


def Evol_donateurs_0_12(data_evolution_0_12):
        # Mappage des couleurs
    color_mapping = {
        'Actifs 0-12 dont PA' : '#0000FF',
        'Actifs 0-12 hors PA' : '#0071C4'}
    # Utiliser le dictionnaire pour créer la liste des couleurs dans le même ordre que les colonnes
    colors_ordered = [color_mapping[col] for col in ['Actifs 0-12 dont PA', 'Actifs 0-12 hors PA']]

    # Vérifier si la police 'Montserrat' est disponible, sinon utiliser une police par défaut
    montserrat_font = "sans-serif"
    for font in findSystemFonts():
        if "Montserrat" in font:
            montserrat_font = "Montserrat"
            break

    # Préparer les données pour le graphique
    x = data_evolution_0_12['Année']  # Les années seront sur l'axe des x
    y_columns = ['Actifs 0-12 dont PA', 'Actifs 0-12 hors PA']

    # Créer le graphique de courbes non empilées avec des marqueurs
    fig, ax = plt.subplots(figsize=(18, 12))  # Adjust these values as needed


    def add_annual_variation_labels_for_PA(ax, data, column_name):
        # Calculer les variations annuelles en pourcentage pour la colonne spécifiée
        annual_variations = data[column_name].pct_change().fillna(0)  # Utiliser fillna(0) pour gérer la première valeur NaN
        # print(annual_variations)  # Pour débogage

        for index, variation_pct in annual_variations.items():
            year = data.loc[index, 'Année']
            # print(f"Année : {year}, Variation : {variation_pct}")  # Pour débogage
            y_pos = data.loc[index, column_name]  # La position verticale est la valeur pour l'année
            if np.isfinite(year) and np.isfinite(y_pos):  # Vérifier si les positions sont finies
                # Déterminer la couleur de l'étiquette en fonction de la variation
                color = 'green' if variation_pct >= 0 else 'red'
                # Ajouter une étiquette de variation annuelle en pourcentage
                ax.text(year, y_pos + 0.18 * y_pos, f'{variation_pct:+.1%}', ha='center', va='bottom', fontsize=10,
                        color=color, fontname=montserrat_font, style='italic')  # Adjusting the position here



    texts = []  # Initialiser une liste pour stocker les objets de texte pour adjustText
    for i, col in enumerate(y_columns):
        values = data_evolution_0_12[col]
        color = color_mapping[col]  # Récupérer la couleur correspondante
        ax.plot(x, values, label=col, color=color, marker='o', linestyle='--', linewidth=1, markersize=6)

        for xi, yi in zip(x, values):
            value_label = f'{int(yi):,}'.replace(',', ' ')  # Format avec séparateur de milliers
            # Placer l'étiquette de valeur avec la couleur correspondante
            texts.append(ax.text(xi, yi - 10000, value_label, ha='center', va='bottom', fontsize=12, fontname=montserrat_font,
                                color=color, fontweight='bold'))
        

    # Ajustements additionnels
    # ax.set_title('Nombre de donateurs uniques par année et type de canal', fontsize=12, fontname=montserrat_font, loc="left")
    # ax.set_xlabel('Année', fontsize=12, fontname=montserrat_font)
    ax.set_xticks(x)  # Faire apparaître chaque année
    ax.set_xticklabels(ax.get_xticks(), fontweight='bold')

    ax.legend(loc='upper left', bbox_to_anchor=(0, 1.3), frameon=False, prop={'family': montserrat_font}) # Changez 1.15 pour ajuster la position verticale
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)  
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False, labelleft=False)  # Retirer les ticks de l'axe des ordonnées

    ax.grid(False)  # Rendre le quadrillage invisible
    ax.yaxis.set_visible(False)  # Cacher la colonne des ordonnées

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname(montserrat_font)

    # adjust_text(texts,
    #             avoid_text=True,  # Les étiquettes évitent de se chevaucher entre elles
    #             avoid_points=True,  # Les étiquettes évitent de se chevaucher avec les points
    #             expand_points=(1.5, 2)
    #             )

    # Ajouter les étiquettes de variation annuelle pour "Actifs 0-12 dont PA"
    add_annual_variation_labels_for_PA(ax, data_evolution_0_12, 'Actifs 0-12 dont PA')

    # Définir les limites de l'axe des ordonnées pour inclure zéro
    ax.set_ylim(0, 180000)

    return ax.figure


