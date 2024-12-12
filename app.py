import os
import shutil
import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from helper import (
    process_note_with_selection,
    collect_entity_windows,
    generate_unique_patterns,
    analyze_embeddings,
    plot_combined_similarity_interactive
)
import plotly.express as px
from datetime import datetime


SUPPORTED_MODELS = {
    "bert-base-uncased": "bert-base-uncased",
    "bert-base-cased": "bert-base-cased",
    "clinicalBERT": "medicalai/ClinicalBERT"
}

def load_model_and_tokenizer(model_name: str):
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Model '{model_name}' is not supported. Available models: {list(SUPPORTED_MODELS.keys())}")
    model_path = SUPPORTED_MODELS[model_name]
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    return model, tokenizer

def clear_resources(file_paths):
    st.cache_data.clear()
    st.cache_resource.clear()

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            st.write(f"Deleted file: {file_path}")
        else:
            st.write(f"File not found: {file_path}")
    
    temp_folder = "temp_files" 
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
        st.write(f"Deleted folder: {temp_folder}")

def main():
    st.title("Embedding Analysis")

    generated_files = []

    st.sidebar.header("Configuration")

    st.sidebar.subheader("Model Selection")
    selected_model = st.sidebar.selectbox("Select Model", list(SUPPORTED_MODELS.keys()))

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

    patterns_output_file = st.sidebar.text_input("Output Patterns File", "patterns.json")
    if not patterns_output_file.strip():
        st.warning("Output patterns file path cannot be empty.")
        return

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
            model, tokenizer = load_model_and_tokenizer(selected_model)
            st.success(f"Loaded model: {selected_model}")
            df_notes = process_note_with_selection(notes_dir, target_phrase)
            if df_notes.empty:
                st.error("No notes processed or target phrase not found. Please check your inputs.")
                return
            st.success("Notes processed successfully!")

            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            folder_name = f"{target_phrase.replace(' ', '-')}-{selected_model}-{window_size}-{current_time}"
            folder_path = os.path.join("output", folder_name)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            modes = ["CPC", "PC", "CP"]
            mode_data_dicts = {}
            for mode in modes:
                st.info(f"Processing mode: {mode}...")

                entity_windows = collect_entity_windows(
                    df_notes,
                    window_size=window_size,
                    mode=mode.lower()
                )

                mode_patterns_file = os.path.join(folder_path, f"patterns_{mode}.json")
                generate_unique_patterns(
                    entity_windows,
                    max_hd=hamming_distance,
                    patterns_per_hd=patterns_per_hd,
                    output_file=mode_patterns_file
                )
                generated_files.append(mode_patterns_file)

                for position in ["start", "middle", "end"]:
                    st.info(f"Analyzing embeddings for position: {position} in mode: {mode}...")

                    embeddings_file = os.path.join(folder_path, f"embeddings_{mode}_{position}.csv")
                    generated_files.append(embeddings_file)
                    df_embeddings = analyze_embeddings(
                        df_notes,
                        target_word_position=position,
                        target_word_index=target_word_index,
                        patterns_file=mode_patterns_file,
                        tokenizer=tokenizer,
                        model=model,
                        mode=mode
                    )

                    df_embeddings.to_csv(embeddings_file, index=False)
                    token = df_embeddings['Token'].iloc[0]
                    
                    st.success(f"Embeddings for mode {mode}, position {position} is avilable")

                    if mode not in mode_data_dicts:
                        mode_data_dicts[mode] = {}
                    mode_data_dicts[mode][position] = df_embeddings

            st.info("Generating similarity plots for all modes...")
            for mode, data_dict in mode_data_dicts.items():
                st.subheader(f"Similarity Plot: Mode {mode}")
                st.text(f"Token(s): {token}")
                fig = plot_combined_similarity_interactive(data_dict, mode)
                image_filename = os.path.join(folder_path, f"similarity_plot_{mode}.png")
                generated_files.append(image_filename)  
                fig.write_image(image_filename)

                st.plotly_chart(fig, use_container_width=True, key=f"plot_{mode}")

                with st.expander(f"View Embedding Data for Mode {mode}", expanded=False):
                    st.subheader(f"Embedding Data for Mode {mode}")
                    for position, df in data_dict.items():
                        st.markdown(f"### {position.capitalize()} Position")
                        st.dataframe(df)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
    
    if st.sidebar.button("Run New Test"):
        clear_resources(generated_files)
        st.success("Cache and files cleared. Ready for a new test!")

if __name__ == "__main__":
    main()
