"""Reference code for dataset preprocessing."""

import pandas as pd
import numpy as np
import re


def preprocess_data():
    """Preprocess and augment datasets to create aug_df.csv (for reference only).

    Returns:
        pd.DataFrame: Augmented dataset.
    
    Raises:
        FileNotFoundError: If raw data files are missing.
    """
    try:
        # Dataset 1
        x = pd.read_csv('trainings.csv', encoding="ISO-8859-1")
        y = pd.read_csv('testing.csv', encoding="ISO-8859-1")
        dup = y[y['Prognosis'].duplicated(keep=False)].sort_values(ascending=True, by='Prognosis')
        unique = dup.groupby('Prognosis').sum()
        uni_gp = unique.reset_index()
        uniques = uni_gp[[col for col in uni_gp.columns if col != 'Prognosis'] + ['Prognosis']]
        uniq = y[~y['Prognosis'].duplicated(keep=False)]
        final_y = pd.concat([uniques, uniq], ignore_index=True)
        df = pd.concat([x, final_y], ignore_index=True)
        dup_df = df[df['Prognosis'].duplicated(keep=False)].sort_values(ascending=True, by='Prognosis', ignore_index=True)
        rem_df = df[~df['Prognosis'].duplicated(keep=False)]
        final_df = pd.concat([dup_df, rem_df], ignore_index=True).sort_values(ascending=True, by='Prognosis', ignore_index=True)
        unique_df = final_df.groupby('Prognosis').sum()
        uniq_df = unique_df.reset_index()
        u_df = uniq_df[[col for col in uniq_df.columns if col != 'Prognosis'] + ['Prognosis']]
        u_df.iloc[:, :-1] = np.where(u_df.iloc[:, :-1]>1, 1, u_df.iloc[:, :-1])
        u_df['Prognosis'] = u_df['Prognosis'].str.replace(r'[\x96\xa0]', ' ', regex=True)

        # Dataset 2
        df2 = pd.read_csv('Final_Augmented_dataset_Diseases_and_Symptoms.csv')
        df2 = df2.rename(columns={'diseases': 'Prognosis'})
        unique_df2 = df2.groupby('Prognosis').sum()
        uniq_df2 = unique_df2.reset_index()
        df2 = uniq_df2[[col for col in uniq_df2.columns if col != 'Prognosis'] + ['Prognosis']]
        df2.iloc[:, :-1] = np.where(df2.iloc[:, :-1]>1, 1, df2.iloc[:, :-1])

        # Combine
        symptoms_df1 = u_df.columns.drop('Prognosis').tolist() 
        symptoms_df2 = df2.columns.drop('Prognosis').tolist()  
        # Create mapping for unification (lowercase comparison)
        sym_to_canonical = {}
        all_symptoms_lower = set([col.lower() for col in symptoms_df1 + symptoms_df2])
        for sym_lower in sorted(all_symptoms_lower):  
            # Find all original names matching this lowercase version
            candidates = [col for col in symptoms_df1 + symptoms_df2 if col.lower() == sym_lower]
            if candidates:
                # Prefer df1 name, then first alphabetically, capitalize
                canonical = next((c for c in candidates if c in symptoms_df1), candidates[0]).capitalize()
                for orig_sym in candidates:           
                    sym_to_canonical[orig_sym] = canonical
        
        # Rename columns in both DataFrames
        df1_mapping = {col: sym_to_canonical[col] for col in symptoms_df1}
        df2_mapping = {col: sym_to_canonical[col] for col in symptoms_df2}
        # Normalize 'Prognosis' to lowercase temporarily for merging
        u_df['Prognosis'] = u_df['Prognosis'].str.lower()
        df2['Prognosis'] = df2['Prognosis'].str.lower()
        df1_renamed = u_df.rename(columns=df1_mapping)
        df2_renamed = df2.rename(columns=df2_mapping)
        
        # Merge DataFrames
        all_symptoms = sorted(set(df1_renamed.columns[:-1]) | set(df2_renamed.columns[:-1]))
        # Expand to all symptoms with 0s where absent
        df1_expanded = df1_renamed.reindex(columns=all_symptoms + ['Prognosis'], fill_value=0)
        df2_expanded = df2_renamed.reindex(columns=all_symptoms + ['Prognosis'], fill_value=0)
        # Concatenate and aggregate by 'Prognosis'
        combined_df = pd.concat([df1_expanded, df2_expanded], ignore_index=True)
        combined_df = combined_df.groupby('Prognosis', as_index=False).max().copy()
        # Capitalize all column names for TabNet
        combined_df.columns = [col.capitalize() for col in combined_df.columns]
        combined_df[all_symptoms] = combined_df[all_symptoms].astype(int)

        # Unify symptom pairs with similar meaning
        symptom_pairs_to_unify = {
            'Abnormal breathing sounds (stridor)': ['Abnormal breathing sounds'],
            'Bed wetting': ['Bedwetting'],
            'Blood in stool': ['Blood in the stool'],
            'Blood in urine': ['Blood in the urine'],
            'Chest tightness or congestion': ['Chest tightness'],
            'Crossed eyes': ['Cross-eyed'],
            'Getting lost on familiar routes': ['Getting lost on familiar routes.1'],
            'Joint stiffness or tightness': ['Joint stiffness'],
            'Leg cramps or spasms': ['Leg cramps'],
            'Muscle stiffness or tightness': ['Muscle stiffness'],
            'Nosebleed': ['Nosebleeds'],
            'Regurgitation': ['Regurgitation.1'],
            'Swelling of abdomen': ['Swollen abdomen'],
            'Swelling of eye': ['Swollen eye'],
            'Tooth pain': ['Toothache'],
        }

        # Create mapping and track columns to drop
        sym_to_unify = {}
        columns_to_drop = []
        combined_df_columns = combined_df.columns.tolist()  

        for preferred, variants in symptom_pairs_to_unify.items():
            if preferred in combined_df_columns:
                for variant in variants:
                    if variant in combined_df_columns:
                        sym_to_unify[variant] = preferred
                        columns_to_drop.append(variant)

        # Unify columns by merging variant into preferred (preserving 1’s)
        for variant, preferred in sym_to_unify.items():
            combined_df[preferred] = combined_df[[preferred, variant]].max(axis=1)

        # Drop the variant columns
        combined_df = combined_df.drop(columns=columns_to_drop)
        combined_df.columns = combined_df.columns.str.replace(r"[\x82\xa0]", " ", regex=True).str.rstrip()
        # Get symptom columns (excluding Prognosis) where all values are 0
        zero_symptom_columns = combined_df.iloc[:, 1:].columns[(combined_df.iloc[:, 1:] == 0).all(axis=0)]
        combined_df = combined_df.drop(columns=zero_symptom_columns)

        # Augment data (due to data scarcity)
        def augment_row(row):
            original_symptoms = np.where(row[1:] == 1)[0]
            n_keep = np.random.randint(max(1, len(original_symptoms) - 2), len(original_symptoms) + 1)
            kept_symptoms = np.random.choice(original_symptoms, n_keep, replace=False)
            new_row = np.zeros(1601, dtype=int)
            new_row[kept_symptoms] = 1
            return np.append(row[0], new_row)

        augmented_data = [row for row in combined_df.values] + [augment_row(row) for row in combined_df.values for _ in range(9)]
        aug_df = pd.DataFrame(augmented_data, columns=combined_df.columns)
        aug_df.iloc[:, 1:] = aug_df.iloc[:, 1:].astype(int)
        aug_df.to_csv("aug_df.csv", index=False)
        return aug_df

    except Exception as e:
        raise RuntimeError(f'Preprocessing failed: {e}')
    

if __name__ == "__main__":
    pass