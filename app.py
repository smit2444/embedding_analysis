# import os
# import streamlit as st
# import pandas as pd
# from transformers import AutoTokenizer, AutoModel
# from helper import (
#     process_note_with_selection,
#     collect_entity_windows,
#     generate_unique_patterns,
#     analyze_embeddings,
#     plot_combined_similarity_interactive
# )
# import matplotlib.pyplot as plt
# import plotly.express as px

# # Supported Models
# SUPPORTED_MODELS = {
#     "bert-base-uncased": "bert-base-uncased",
#     "bert-base-cased": "bert-base-cased",
#     "clinicalBERT": "medicalai/ClinicalBERT"
# }

# def load_model_and_tokenizer(model_name: str):
#     if model_name not in SUPPORTED_MODELS:
#         raise ValueError(f"Model '{model_name}' is not supported. Available models: {list(SUPPORTED_MODELS.keys())}")
#     model_path = SUPPORTED_MODELS[model_name]
#     tokenizer = AutoTokenizer.from_pretrained(model_path)
#     model = AutoModel.from_pretrained(model_path)
#     return model, tokenizer

# def main():
#     st.title("Embedding Analysis")

#     # Sidebar for configuration
#     st.sidebar.header("Configuration")

#     # Step 1: Model Selection
#     st.sidebar.subheader("Model Selection")
#     selected_model = st.sidebar.selectbox("Select Model", list(SUPPORTED_MODELS.keys()))
#     model, tokenizer = load_model_and_tokenizer(selected_model)
#     st.success(f"Loaded model: {selected_model}")

#     # Step 2: Analysis Parameters
#     st.sidebar.subheader("Analysis Parameters")
#     window_size = st.sidebar.slider("Window Size", 5, 30, 10)

#     target_phrase = st.sidebar.text_input("Enter Target Phrase")
#     if not target_phrase:
#         st.warning("Target phrase cannot be empty.")
#         return

#     target_phrase_length = len(target_phrase.split())
#     target_word_index = st.sidebar.number_input(
#         "Target Word Index in Target Phrase",
#         0,
#         max(target_phrase_length - 1, 0),
#         0
#     )

#     max_hamming_distance = max(window_size - target_phrase_length, 0)
#     hamming_distance = st.sidebar.slider(
#         "Max Hamming Distance",
#         0,
#         max_hamming_distance,
#         max_hamming_distance
#     )
#     patterns_per_hd = st.sidebar.number_input("Patterns per Hamming Distance", min_value=1, max_value=40, value=5)

#     patterns_output_file = st.sidebar.text_input("Output Patterns File", "patterns.json")
#     if not patterns_output_file.strip():
#         st.warning("Output patterns file path cannot be empty.")
#         return

#     st.sidebar.subheader("File Selection")
#     preloaded_dir = "./notes"
#     preloaded_files = [
#         f for f in os.listdir(preloaded_dir) if os.path.isfile(os.path.join(preloaded_dir, f)) and f.endswith(".txt")
#     ]

#     if not preloaded_files:
#         st.error(f"No .txt files found in the preloaded folder: {preloaded_dir}")
#         return

#     selected_files = st.sidebar.multiselect("Select Files for Analysis", preloaded_files)
#     if not selected_files:
#         st.warning("Please select at least one file for analysis.")
#         return

#     notes_dir = [os.path.join(preloaded_dir, f) for f in selected_files]

#     if st.sidebar.button("Perform Analysis"):
#         try:
#             # Process notes
#             df_notes = process_note_with_selection(notes_dir, target_phrase)
#             if df_notes.empty:
#                 st.error("No notes processed or target phrase not found. Please check your inputs.")
#                 return
#             st.success("Notes processed successfully!")

#             # Extract context windows and perform analysis for each mode
#             modes = ["CPC", "PC", "CP"]
#             mode_data_dicts = {}
#             for mode in modes:
#                 st.info(f"Processing mode: {mode}...")

#                 # Extract context windows
#                 entity_windows = collect_entity_windows(
#                     df_notes,
#                     window_size=window_size,
#                     mode=mode.lower()
#                 )

#                 # Generate unique patterns for this mode
#                 mode_patterns_file = f"patterns_{mode}.json"
#                 generate_unique_patterns(
#                     entity_windows,
#                     max_hd=hamming_distance,
#                     patterns_per_hd=patterns_per_hd,
#                     output_file=mode_patterns_file
#                 )

#                 # Analyze embeddings for each position and save them to unique files
#                 for position in ["start", "middle", "end"]:
#                     st.info(f"Analyzing embeddings for position: {position} in mode: {mode}...")

#                     embeddings_file = f"embeddings_{mode}_{position}.csv"
#                     df_embeddings = analyze_embeddings(
#                         df_notes,
#                         target_word_position=position,
#                         target_word_index=target_word_index,
#                         patterns_file=mode_patterns_file,
#                         tokenizer=tokenizer,
#                         model=model
#                     )

#                     # Save the embeddings to a file
#                     df_embeddings.to_csv(embeddings_file, index=False)
#                     st.success(f"Embeddings for mode {mode}, position {position} saved to {embeddings_file}")

#                     # Store in data dictionary for plotting (optional)
#                     if mode not in mode_data_dicts:
#                         mode_data_dicts[mode] = {}
#                     mode_data_dicts[mode][position] = df_embeddings

#             # Generate and display plots for all modes
#             st.info("Generating similarity plots for all modes...")
#             for mode, data_dict in mode_data_dicts.items():
#                 st.subheader(f"Similarity Plot: Mode {mode}")
#                 fig = plot_combined_similarity_interactive(data_dict, mode)
#                 # st.plotly_chart(fig)
#                 image_filename = f"similarity_plot_{mode}.png"
#                 fig.write_image(image_filename)

#                 # Step 2: Display the plot in Streamlit and view csv
#                 st.plotly_chart(fig, use_container_width=True, key=f"plot_{mode}")

#                 with st.expander(f"View Embedding Data for Mode {mode}", expanded=False):
#                     st.subheader(f"Embedding Data for Mode {mode}")
#                     for position, df in data_dict.items():
#                         st.markdown(f"### {position.capitalize()} Position")
#                         st.dataframe(df)

#         except Exception as e:
#             st.error(f"An error occurred during processing: {e}")


# if __name__ == "__main__":
#     main()

import os
import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from datetime import datetime  # For timestamping
from helper import (
    process_note_with_selection,
    collect_entity_windows,
    generate_unique_patterns,
    analyze_embeddings,
    plot_combined_similarity_interactive
)
import matplotlib.pyplot as plt
import plotly.express as px

# Supported Models
SUPPORTED_MODELS = {
    "bert-base-uncased": "bert-base-uncased",
    "bert-base-cased": "bert-base-cased",
    "clinicalBERT": "medicalai/ClinicalBERT"
}

# Directory for persistent storage in Hugging Face Spaces
PERSISTENT_DIR = "/persistent"  # Hugging Face Spaces' persistent directory

def load_model_and_tokenizer(model_name: str):
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Model '{model_name}' is not supported. Available models: {list(SUPPORTED_MODELS.keys())}")
    model_path = SUPPORTED_MODELS[model_name]
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    return model, tokenizer

def create_run_directory(model_name, window_size, target_word):
    """Create a directory for the current run based on model, window size, and target word."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"{model_name} - window {window_size} - {target_word} - {timestamp}"
    run_dir_path = os.path.join(PERSISTENT_DIR, run_dir)
    os.makedirs(run_dir_path, exist_ok=True)
    return run_dir_path

def main():
    st.title("Embedding Analysis")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Step 1: Model Selection
    st.sidebar.subheader("Model Selection")
    selected_model = st.sidebar.selectbox("Select Model", list(SUPPORTED_MODELS.keys()))
    model, tokenizer = load_model_and_tokenizer(selected_model)
    st.success(f"Loaded model: {selected_model}")

    # Step 2: Analysis Parameters
    st.sidebar.subheader("Analysis Parameters")
    window_size = st.sidebar.slider("Window Size", 5, 30, 10)

    target_phrase = st.sidebar.text_input("Enter Target Phrase")
    if not target_phrase:
        st.warning("Target phrase cannot be empty.")
        return

    target_phrase_length = len(target_phrase.split())
    target_word_index = st.sidebar.number_input(
        "Target Word Index in Target Phrase",
        0,
        max(target_phrase_length - 1, 0),
        0
    )

    max_hamming_distance = max(window_size - target_phrase_length, 0)
    hamming_distance = st.sidebar.slider(
        "Max Hamming Distance",
        0,
        max_hamming_distance,
        max_hamming_distance
    )
    patterns_per_hd = st.sidebar.number_input("Patterns per Hamming Distance", min_value=1, max_value=40, value=5)

    st.sidebar.subheader("File Selection")
    preloaded_dir = "./notes"
    preloaded_files = [
        f for f in os.listdir(preloaded_dir) if os.path.isfile(os.path.join(preloaded_dir, f)) and f.endswith(".txt")
    ]

    if not preloaded_files:
        st.error(f"No .txt files found in the preloaded folder: {preloaded_dir}")
        return

    selected_files = st.sidebar.multiselect("Select Files for Analysis", preloaded_files)
    if not selected_files:
        st.warning("Please select at least one file for analysis.")
        return

    notes_dir = [os.path.join(preloaded_dir, f) for f in selected_files]

    if st.sidebar.button("Perform Analysis"):
        try:
            # Create a directory for this run
            run_directory = create_run_directory(selected_model, window_size, target_phrase)
            st.success(f"Results will be saved in: {run_directory}")

            # Process notes
            df_notes = process_note_with_selection(notes_dir, target_phrase)
            if df_notes.empty:
                st.error("No notes processed or target phrase not found. Please check your inputs.")
                return
            st.success("Notes processed successfully!")

            # Extract context windows and perform analysis for each mode
            modes = ["CPC", "PC", "CP"]
            mode_data_dicts = {}
            for mode in modes:
                st.info(f"Processing mode: {mode}...")

                # Extract context windows
                entity_windows = collect_entity_windows(
                    df_notes,
                    window_size=window_size,
                    mode=mode.lower()
                )

                # Generate unique patterns for this mode
                mode_patterns_file = os.path.join(run_directory, f"patterns_{mode}.json")
                generate_unique_patterns(
                    entity_windows,
                    max_hd=hamming_distance,
                    patterns_per_hd=patterns_per_hd,
                    output_file=mode_patterns_file
                )

                # Analyze embeddings for each position and save them to unique files
                for position in ["start", "middle", "end"]:
                    st.info(f"Analyzing embeddings for position: {position} in mode: {mode}...")

                    embeddings_file = os.path.join(run_directory, f"embeddings_{mode}_{position}.csv")
                    df_embeddings = analyze_embeddings(
                        df_notes,
                        target_word_position=position,
                        target_word_index=target_word_index,
                        patterns_file=mode_patterns_file,
                        tokenizer=tokenizer,
                        model=model
                    )

                    # Save the embeddings to a file
                    df_embeddings.to_csv(embeddings_file, index=False)
                    st.success(f"Embeddings for mode {mode}, position {position} saved to {embeddings_file}")

                    # Store in data dictionary for plotting (optional)
                    if mode not in mode_data_dicts:
                        mode_data_dicts[mode] = {}
                    mode_data_dicts[mode][position] = df_embeddings

            # Generate and display plots for all modes
            st.info("Generating similarity plots for all modes...")
            for mode, data_dict in mode_data_dicts.items():
                st.subheader(f"Similarity Plot: Mode {mode}")
                fig = plot_combined_similarity_interactive(data_dict, mode)
                plot_file = os.path.join(run_directory, f"similarity_plot_{mode}.png")
                fig.write_image(plot_file)
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()
