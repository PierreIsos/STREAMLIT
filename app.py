import streamlit as st
import pandas as pd
import numpy as np
from matplotlib.font_manager import findfont, FontProperties, findSystemFonts
from matplotlib.colors import LinearSegmentedColormap
from calculs import structure_base, structure_base_nat, structure_base_fede, flux_donateur, flux_donateur_nat, flux_donateur_fede, flux_donateur_PA, flux_donateur_WEB
from calculs import data_evolution, data_evolution_0_12
import matplotlib.pyplot as plt
from graphiques import generate_graphs, generate_stacked_bar_chart, PA_chart, WEB_chart
from graphiques import Evol_donateurs, Evol_donateurs_0_12

st.set_page_config(page_title='SPFxISK' ,page_icon='👨‍🔬')

# Créer des onglets pour chaque section
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Profiling", "Chiffres clés", "Evolution de la base", "Focus", "Recrutement"])

# Créer un exemple de données pour afficher un graphique
np.random.seed(0)
data = pd.DataFrame(
    np.random.randn(10, 2),
    columns=["X", "Y"]
)

# Afficher le contenu de chaque section dans l'onglet correspondant
with tab1:
    # Créer une liste déroulante pour sélectionner la sous-section
    sous_sections = ["PA", "Web", "Dons ponctuels"]
    sous_section = st.selectbox("Sous-section", sous_sections)

    # Afficher le contenu de type graphique en fonction de la sous-section sélectionnée
    if sous_section == "PA":
        st.line_chart(data)
    elif sous_section == "Web":
        st.area_chart(data)
    elif sous_section == "Dons ponctuels":
        st.bar_chart(data)


# Dans votre tab2
with tab2:
    # Sélection de l'option pour le premier graphique
    selected_option = st.selectbox("Sélectionnez le type de donateur :", ('Tous les donateurs', 'National', 'Fédération'))
    
    # Sélection de l'année pour le premier graphique
    selected_year_1 = st.radio("Sélectionnez l'année :", ('2022', '2021'))

    # Modifier structure_base en fonction de l'option sélectionnée pour le premier graphique
    if selected_option == 'National':
        structure_base = structure_base_nat
    elif selected_option == 'Fédération':
        structure_base = structure_base_fede
    elif selected_option == 'Tous les donateurs':
        structure_base = structure_base 

    # Titre pour le premier graphique
    st.markdown(f"<p style='font-size:24px; font-weight:bold; text-align:center;'>Structure de la base des donateurs {selected_option} en {selected_year_1}</p>", unsafe_allow_html=True)

    # Call the function to generate the first graph
    fig1 = generate_graphs(structure_base, selected_year_1)
    st.pyplot(fig1)

    # Ajoutez un espace entre les graphiques
    st.write("")
    
    # Sélection de l'option pour le deuxième graphique
    selected_option2 = st.selectbox("Sélectionnez le type de donateur : ", ('Tous les donateurs', 'National', 'Fédération'))
    
    # Modifier flux_donateur en fonction de l'option sélectionnée pour le deuxième graphique
    if selected_option2 == 'National':
        flux_donateur = flux_donateur_nat
    elif selected_option2 == 'Fédération':
        flux_donateur = flux_donateur_fede
    elif selected_option2 == 'Tous les donateurs':
        flux_donateur = flux_donateur 

    # Titre pour le deuxième graphique
    st.markdown(f"<p style='font-size:24px; font-weight:bold; text-align:center;'>Les flux de donateurs {selected_option2}</p>", unsafe_allow_html=True)

    # Call the function to generate the second graph
    fig2 = generate_stacked_bar_chart(flux_donateur)
    st.pyplot(fig2)

    # Ajoutez un espace entre les graphiques
    st.write("")

    # Titre pour le troisieme graphique
    st.markdown(f"<p style='font-size:24px; font-weight:bold; text-align:center;'>Les flux de donateurs PA</p>", unsafe_allow_html=True)

    # Call the function to generate the second graph
    fig3 = PA_chart(flux_donateur_PA)
    st.pyplot(fig3)

    # Ajoutez un espace entre les graphiques
    st.write("")
    
    # Titre pour le troisieme graphique
    st.markdown(f"<p style='font-size:24px; font-weight:bold; text-align:center;'>Les flux de donateurs WEB</p>", unsafe_allow_html=True)

    # Call the function to generate the second graph
    fig4 = WEB_chart(flux_donateur_WEB)
    st.pyplot(fig4)


# Dans votre tab3
with tab3:
    # Afficher le contenu de la section "Evolution de la base"
    # Sélection de l'option pour le deuxième graphique
    selected_option3 = st.selectbox("Sélectionnez le laps de temps souhaité :", ('0-12', '0-24'))
    
    # Modifier flux_donateur en fonction de l'option sélectionnée pour le deuxième graphique
    if selected_option3 == '0-12':
        data_evolution_selected = data_evolution_0_12
        graph_function = Evol_donateurs_0_12
    elif selected_option3 == '0-24':
        data_evolution_selected = data_evolution
        graph_function = Evol_donateurs

    # Titre pour le premier graphique
    st.markdown(f"<p style='font-size:24px; font-weight:bold; text-align:center;'>Evolution de la base des actifs {selected_option3}</p>", unsafe_allow_html=True)

    # Call the function to generate the first graph
    fig5 = graph_function(data_evolution_selected)
    st.pyplot(fig5)



with tab4:
    # Créer une liste déroulante pour sélectionner la sous-section
    sous_sections = ["PA", "Web", "Dons boutiques"]
    sous_section = st.selectbox("Sous-section", sous_sections)

    # Afficher le contenu de type graphique en fonction de la sous-section sélectionnée
    if sous_section == "PA":
        st.line_chart(data)
    elif sous_section == "Web":
        st.area_chart(data)
    elif sous_section == "Dons boutiques":
        st.bar_chart(data)

with tab5:
    # Créer une liste déroulante pour sélectionner la sous-section
    sous_sections = ["Normal", "Urgences"]
    sous_section = st.selectbox("Sous-section", sous_sections)

    # Afficher le contenu de type graphique en fonction de la sous-section sélectionnée
    if sous_section == "Normal":
        st.line_chart(data)
    elif sous_section == "Urgences":
        st.area_chart(data)


