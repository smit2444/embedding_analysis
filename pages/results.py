import os
import streamlit as st
import pandas as pd
from helper import plot_combined_similarity_interactive  
import plotly.express as px

def display_saved_results():
    experiments_dir = "./output"
    
    experiment_folders = [f for f in os.listdir(experiments_dir) if os.path.isdir(os.path.join(experiments_dir, f))]
    
    if not experiment_folders:
        st.error("No experiments found.")
        return
    
    selected_experiment = st.selectbox("Select Experiment", experiment_folders)
    experiment_folder_path = os.path.join(experiments_dir, selected_experiment)
    
    generated_files = [f for f in os.listdir(experiment_folder_path) if os.path.isfile(os.path.join(experiment_folder_path, f))]
    
    similarity_plots = [f for f in generated_files if f.startswith("similarity_plot")]
    embeddings_files = [f for f in generated_files if f.startswith("embeddings")]
    
    if not embeddings_files:
        st.error("No embeddings files found in the selected experiment.")
        return

    mode_data_dicts = {}

    for embeddings_file in embeddings_files:
        parts = embeddings_file.split('_')
        if len(parts) != 3:
            continue 
        mode = parts[1]
        position = parts[2].replace('.csv', '')  # Extract position ('start', 'middle', 'end')

        # Read the embeddings file
        embeddings_file_path = os.path.join(experiment_folder_path, embeddings_file)
        df_embeddings = pd.read_csv(embeddings_file_path)
        
        # Organize the data into the mode_data_dicts dictionary
        if mode not in mode_data_dicts:
            mode_data_dicts[mode] = {}
        mode_data_dicts[mode][position] = df_embeddings

    # Use plot_combined_similarity_interactive to plot the results
    st.info("Generating similarity plots for all modes...")
    for mode, data_dict in mode_data_dicts.items():
        st.subheader(f"Similarity Plot: Mode {mode}")
        
        # Ensure all 3 required files (start, middle, end) are present
        if 'start' in data_dict and 'middle' in data_dict and 'end' in data_dict:
            # Use the three dataframes for the plot
            fig = plot_combined_similarity_interactive(data_dict, mode)
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True, key=f"plot_{mode}")
            
            # Display the CSV data below the plot
            with st.expander(f"View Embedding Data for Mode {mode}", expanded=False):
                st.subheader(f"Embedding Data for Mode {mode}")
                expected_order = ["start", "middle", "end"]

                sorted_data = {pos: data_dict[pos] for pos in expected_order if pos in data_dict}

                for position, df in sorted_data.items():
                    st.markdown(f"### {position.capitalize()} Position")
                    st.dataframe(df)
        else:
            st.warning(f"Not all required files (start, middle, end) found for Mode {mode}. Skipping plot generation.")

if __name__ == "__main__":
    display_saved_results()

