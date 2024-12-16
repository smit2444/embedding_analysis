import re
import numpy as np
from itertools import combinations
import random
import json
import os
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
def read_notes(folder_path):
    notes = []
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                with open(os.path.join(folder_path, filename), 'r') as file:
                    notes.append((filename, file.read()))
    return notes
def process_note_with_selection(file_paths, target_phrase):
    results = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            selected_entities = []
            indices = []
            start_idx = content.find(target_phrase)
            while start_idx != -1:
                indices.append(start_idx)
                start_idx = content.find(target_phrase, start_idx + 1)
            if not indices:
                st.warning(f"'{target_phrase}' not found in file '{os.path.basename(file_path)}'.")
            else:
                selected_entities.append((target_phrase, indices))
            results.append({
                'Filename': os.path.basename(file_path),
                'Content': content,
                'Selected Entities': selected_entities
            })
        except Exception as e:
            st.error(f"Error processing file {file_path}: {e}")
    return pd.DataFrame(results)
def get_target_word_embedding(context, target_word, tokenizer, model):
    inputs = tokenizer(context, return_tensors="pt", padding=True, truncation=True, max_length=1000)
    with torch.no_grad():
        outputs = model(**inputs)
    word_embeddings = outputs.last_hidden_state.squeeze(0)
    tokens = tokenizer.tokenize(context)
    target_word_tokens = tokenizer.tokenize(target_word)
    print(target_word_tokens)
    target_token_ids = tokenizer.convert_tokens_to_ids(target_word_tokens)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    token_indices = [i for i in range(len(token_ids)) if token_ids[i:i + len(target_token_ids)] == target_token_ids]
    if token_indices:
        word_embedding = word_embeddings[token_indices[0]:token_indices[0] + len(target_token_ids)].mean(dim=0).numpy()
    else:
        word_embedding = word_embeddings.mean(dim=0).numpy()
    return word_embedding, target_word_tokens

def collect_entity_windows(df, window_size=10, mode='cpc'):
    """
    Collect context windows for each entity in the DataFrame.
    """
    entity_windows_dict = {}

    for _, row in df.iterrows():
        content = row['Content']
        filename = row.get('Filename', 'Unknown')

        for entity_info in row['Selected Entities']:
            if isinstance(entity_info, tuple) and len(entity_info) == 2:
                entity, _ = entity_info
            else:
                entity = entity_info

            # Extract context windows
            windows = extract_context_windows(content, entity, window_size, mode)
            if entity not in entity_windows_dict:
                entity_windows_dict[entity] = []
            entity_windows_dict[entity].extend(windows)
    return entity_windows_dict
def extract_context_windows(text, target_phrase, window_size, mode='cpc'):
    words = text.split()
    windows = []
    phrase_words = target_phrase.split()
    phrase_length = len(phrase_words)

    context_size = window_size - phrase_length if mode == 'cpc' else window_size
    half_context = context_size // 2

    def find_phrase_indices(text, target_phrase):
        words = text.split()
        phrase_words = target_phrase.split()
        phrase_len = len(phrase_words)
        indices = []
        for i in range(len(words) - phrase_len + 1):
            if words[i:i + phrase_len] == phrase_words:
                indices.append(i)
        return indices

    indices = find_phrase_indices(text, target_phrase)

    for target_index in indices:
        if mode == 'cpc':  # Context-Phrase-Context
            start_index = max(0, target_index - half_context)
            end_index = min(len(words), target_index + phrase_length + half_context)

            context_before = words[start_index:target_index]
            context_after = words[target_index + phrase_length:end_index]
            context_total = context_before + phrase_words + context_after

            if len(context_total) > window_size:
                excess = len(context_total) - window_size
                if len(context_after) >= excess:
                    context_after = context_after[:-excess]
                else:
                    excess -= len(context_after)
                    context_before = context_before[excess:]

                context_total = context_before + phrase_words + context_after

            remove_target_phrase = [
                word for word in context_total if word not in phrase_words
            ]
            windows.append(' '.join(remove_target_phrase))

        elif mode == 'pc':
            start_index = target_index
            end_index = min(len(words), target_index + phrase_length + context_size)

            if end_index > len(words):
                end_index = len(words)

            context_before = words[start_index:target_index]
            context_after = words[target_index + phrase_length:end_index]

            context_total = context_before + phrase_words + context_after

            if len(context_total) > window_size:
                context_total = context_total[:window_size]  # Truncate from the start if too long

            context_total = context_total[len(phrase_words):]  # Remove the target phrase from the beginning

            windows.append(' '.join(context_total))
        elif mode == 'cp':
            start_index = max(0, target_index - (window_size - phrase_length))
            end_index = target_index + phrase_length

            if start_index < 0:
                start_index = 0
            context_before = words[start_index:target_index]
            context_after = words[target_index + phrase_length:end_index]

            context_total = context_before + phrase_words + context_after

            if len(context_total) > window_size:
                excess = len(context_total) - window_size
                context_total = context_total[:-excess]  # Truncate from the end

            context_total = context_total[:-len(phrase_words)]

            windows.append(' '.join(context_total))
    return windows

def calculate_hamming_distance(seq1, seq2):
    """
    Calculate the Hamming distance between two sequences.
    """
    return sum(el1 != el2 for el1, el2 in zip(seq1, seq2))

def generate_patterns_with_hamming_distance(words, hamming_distance, pattern_limit, all_patterns):
    """
    Generate unique patterns based on an exact Hamming distance for a given list of words.
    Ensures no duplicate patterns across different Hamming distances.
    """
    patterns = set()
    original_words = words.copy()

    # Generate patterns by swapping exactly `hamming_distance` positions
    while len(patterns) < pattern_limit:
        new_pattern = original_words.copy()

        # Select `hamming_distance` unique positions to change
        indices_to_swap = random.sample(range(len(new_pattern)), hamming_distance)

        # Shuffle the selected indices to create the desired pattern
        swapped_words = [new_pattern[i] for i in indices_to_swap]
        random.shuffle(swapped_words)

        # Apply the swaps to the new pattern
        for idx, new_word in zip(indices_to_swap, swapped_words):
            new_pattern[idx] = new_word

        # Convert to string and ensure uniqueness
        pattern_str = ' '.join(new_pattern)

        # Check for duplicates and exact Hamming distance from original
        if (pattern_str not in patterns and
            pattern_str not in all_patterns and
            calculate_hamming_distance(original_words, new_pattern) == hamming_distance):
            patterns.add(pattern_str)
            all_patterns.add(pattern_str)

    return list(patterns)
def generate_unique_patterns(entity_windows_dict, max_hd=4, patterns_per_hd=5, output_file='patterns.json'):
    patterns_dict = {}

    for entity, windows in entity_windows_dict.items():
        patterns_dict[entity] = []

        for window in windows:
            window_patterns = {'original_window': window, 'patterns_by_hd': {}}
            window_words = window.split()
            all_patterns = set()
            for hd in range(2, max_hd + 1):
                # Generate `patterns_per_hd` unique patterns for each Hamming distance
                hd_patterns = generate_patterns_with_hamming_distance(window_words, hd, patterns_per_hd, all_patterns)
                window_patterns['patterns_by_hd'][f'hd_{hd}'] = hd_patterns

            patterns_dict[entity].append(window_patterns)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns_dict, f, ensure_ascii=False, indent=4)

    print(f"Patterns saved to '{output_file}'")
    return patterns_dict


def load_patterns_per_entity(patterns_file='patterns.json'):

    if not os.path.exists(patterns_file):
        raise FileNotFoundError(f"The patterns file '{patterns_file}' does not exist. Please generate it first by running 'generate_unique_patterns'.")
    with open(patterns_file, 'r', encoding='utf-8') as f:
        patterns_dict = json.load(f)
    return patterns_dict

def analyze_embeddings(df, target_word_position='end', target_word_index=0, patterns_file='patterns.json', tokenizer=None, model=None, mode='CPC', phrase_size=4, reversed=False):
    embedding_analysis = []

    # Load patterns per entity from the saved file
    with open(patterns_file, 'r', encoding='utf-8') as f:
        patterns_dict = json.load(f)

    for _, row in df.iterrows():
        filename = row.get('Filename', 'Unknown')

        for entity_info in row['Selected Entities']:
            if isinstance(entity_info, tuple) and len(entity_info) == 2:
                entity, _ = entity_info  # Target phrase (entity)
            else:
                entity = entity_info

            print(f"\nProcessing entity: '{entity}' from file '{filename}'")

            # Get patterns and original window for this entity
            unique_patterns = patterns_dict.get(entity, [])
            if not unique_patterns:
                continue

            for window_data in unique_patterns:
                original_window = window_data['original_window']
                print(f"Original window: '{original_window}'")

                # Treat the target phrase (entity) as a unit (don't split it)
                entity_words = entity.split()  # Split the target phrase into words

                # Check if the target_word_index is valid
                if target_word_index < len(entity_words):
                    target_word = entity_words[target_word_index]  # Get the target word at the specified index
                    print(f"Selected target word: '{target_word}' from the target phrase: '{entity}'")
                else:
                    print(f"Error: Target word index {target_word_index} is out of bounds for the target phrase: '{entity}'")
                    continue
                # For adding target word at every possible position depending on the length of phrase
                for target_word_position_in_phrase in range(phrase_size):
                    rearranged_entity_words = entity_words[:]
                    rearranged_entity_words.remove(target_word)  
                    target_position = min(target_word_position_in_phrase, len(rearranged_entity_words))
                    rearranged_entity_words.insert(target_position, target_word)
                    rearranged_entity = ' '.join(rearranged_entity_words)
                # For adding the target word at 3 positions
                # for target_word_position_in_phrase in ['start', 'middle', 'end']:
                #     # print(f"\nAnalyzing target word at the {target_word_position_in_phrase} of the phrase")

                #     # Copy the original target phrase
                #     rearranged_entity_words = entity_words[:]

                #     # Move the target word to the specified position
                #     rearranged_entity_words.remove(target_word)  # Remove the target word from its original position
                #     if target_word_position_in_phrase == 'start':
                #         rearranged_entity_words.insert(0, target_word)
                #     elif target_word_position_in_phrase == 'middle':
                #         middle_index = len(rearranged_entity_words) // 2
                #         rearranged_entity_words.insert(middle_index, target_word)
                #     elif target_word_position_in_phrase == 'end':
                #         rearranged_entity_words.append(target_word)

                #     rearranged_entity = ' '.join(rearranged_entity_words)
                    # print(f"Rearranged target phrase: '{rearranged_entity}'")

                    # Add rearranged target phrase to the original window based on position
                    original_words = original_window.split()
                    if mode == 'PC':
                        original_words = entity_words + original_words
                    elif mode == 'CP':
                        original_words = original_words + entity_words
                    elif mode == 'CPC':
                        middle_index = len(original_words) // 2
                        original_words = original_words[:middle_index] + entity_words + original_words[middle_index:]

                    modified_window = ' '.join(original_words)
                    # print(f"Modified window with rearranged target phrase: '{modified_window}'")

                    # Get the embedding for the target word in this modified window
                    # print(f"Computing embedding for the target word '{target_word}' in the context of the modified window with rearranged phrase")
                    original_embedding, original_tokens = get_target_word_embedding(modified_window, target_word=target_word, tokenizer=tokenizer, model=model) #original window

                    # Calculate cosine similarities with patterns at each Hamming distance
                    for hd, patterns in window_data['patterns_by_hd'].items():
                        # print(f"Processing Hamming Distance: {hd}")
                        for pattern in patterns:
                            # print(f"Pattern before modification: '{pattern}'")

                            # Adjust each pattern by adding the rearranged target phrase at the specified position
                            pattern_words = pattern.split()
                            if target_word_position == 'start':
                                pattern_words = rearranged_entity_words + pattern_words
                            elif target_word_position == 'end':
                                pattern_words = pattern_words + rearranged_entity_words
                            elif target_word_position == 'middle':
                                middle_index = len(pattern_words) // 2
                                pattern_words = pattern_words[:middle_index] + rearranged_entity_words + pattern_words[middle_index:]

                            adjusted_pattern = ' '.join(pattern_words)

                            # Reversed condition, makes the entire adjusted_pattern to be reversed and will be compared with original window
                            if reversed == True:
                                adjusted_pattern = ' '.join(adjusted_pattern.split()[::-1])

                            # Get embedding for the rearranged target word in the adjusted pattern
                            # print(f"Computing embedding for the target word '{target_word}' in the adjusted pattern: '{adjusted_pattern}'")
                            pattern_embedding, pattern_tokens = get_target_word_embedding(adjusted_pattern, target_word=target_word, tokenizer=tokenizer, model=model)

                            # Compute cosine similarity between the original and rearranged pattern embeddings
                            cs_similarity = cosine_similarity([original_embedding], [pattern_embedding])[0][0]
                            euclidean_distance = np.linalg.norm(np.array(original_embedding) - np.array(pattern_embedding))

                            # print(f"Cosine similarity: {similarity}")

                            # Append result to the analysis list
                            embedding_analysis.append({
                                'Filename': filename,
                                'Original Phrase': ' '.join(entity_words),
                                'Rearranged Phrase': rearranged_entity,
                                'Target Word': target_word,
                                'Reversed': reversed,
                                'Position': target_word_position_in_phrase,
                                'Hamming Distance': int(hd.split('_')[1]),
                                'Context': original_window,
                                'Original Window': modified_window, # modified_window is simply the original_window + target phrase that is obtained from the reference
                                'Variation Window': adjusted_pattern,
                                'Similarity': cs_similarity,
                                'Euclidean Distance': euclidean_distance,
                                'Token': original_tokens
                            })
    return pd.DataFrame(embedding_analysis)


# def plot_combined_similarity_interactive(data_dict, mode):
#     import plotly.graph_objects as go
#     import plotly.express as px

#     # Use a color scale for dynamic color assignment (e.g., 'Viridis', 'Rainbow', etc.)
#     color_scale = px.colors.qualitative.Set1  # Can also use 'Viridis', 'Rainbow', etc.
#     entity_styles = {
#         'start': 'solid',
#         'middle': 'dash',
#         'end': 'dot'
#     }
   

#     # Sort data_dict by numeric position order
#     sorted_data = {k: data_dict[k] for k in sorted(data_dict.keys())}

#     # Gather unique windows
#     original_windows = set().union(*[df['Original Window'].unique() for df in sorted_data.values()])
#     fig = go.Figure()

#     # Iterate through windows
#     for original_window in original_windows:
#         # Iterate through sorted entity positions
#         for entity_position, df in sorted_data.items():
#             window_df = df[df['Original Window'] == original_window]
#             if window_df.empty:
#                 continue  
#             # Get unique numeric positions (can be dynamic)
#             unique_positions = sorted(window_df['Position'].unique())

#             # Iterate through numeric target word positions (dynamic)
#             for idx, target_word_position in enumerate(unique_positions):
#                 position_group_df = window_df[window_df['Position'] == target_word_position]
#                 if position_group_df.empty:
#                     continue 
                
#                 # Map target word position to a color from the color scale
#                 color = color_scale[idx % len(color_scale)]  # Ensure colors loop if more than available

#                 # Aggregate statistics
#                 similarity_stats = position_group_df.groupby('Hamming Distance')['Similarity'].mean().reset_index()
                
#                 # Add trace
#                 fig.add_trace(go.Scatter(
#                     x=similarity_stats['Hamming Distance'],
#                     y=similarity_stats['Similarity'],
#                     mode='lines+markers', 
#                     name=f"Target Word Position: {target_word_position}, Phrase Position: {entity_position}",
#                     line=dict(color=color, dash=entity_styles[entity_position]),  # You can customize line styles further if needed
#                     marker=dict(
#                         size=10,  
#                         color=color,  
#                         opacity=0.6  
#                     ),
#                     text=similarity_stats.apply(
#                         lambda row: f"Original Window: {original_window}<br>Hamming Distance: {row['Hamming Distance']}<br>Similarity: {row['Similarity']:.2f}",
#                         axis=1 
#                     ),
#                     hoverinfo='text'  
#                 ))

#     # Configure layout
#     fig.update_layout(
#         title=f"Combined Cosine Similarity by Hamming Distance\nOriginal Window: '{original_window}' - RPP: {mode}",
#         xaxis_title="Hamming Distance",
#         yaxis_title="Mean Cosine Similarity",
#         yaxis=dict(
#             range=[0, 1], 
#             tickmode='array',  
#             tickvals=[i / 10 for i in range(11)], 
#             ticktext=[f"{i / 10:.1f}" for i in range(11)]  
#         ),
#         template="plotly_white",  
#         hovermode='closest', 
#         legend=dict(x=1.1, y=1),  
#         margin=dict(r=150, t=100, b=50, l=50),  
#     )

#     # Update trace and interactivity settings
#     fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))  
#     fig.update_layout(
#         clickmode='event+select',
#     )

#     fig.show()
#     return fig

def plot_combined_similarity_interactive(data_dict, mode):
    import plotly.graph_objects as go
    import plotly.express as px

    # Use a color scale for dynamic color assignment
    color_scale = px.colors.qualitative.Set1
    entity_styles = {
        'start': 'solid',
        'middle': 'dash',
        'end': 'dot'
    }

    # Sort data_dict by numeric position order
    sorted_data = {k: data_dict[k] for k in sorted(data_dict.keys())}

    # Gather unique windows
    original_windows = set().union(*[df['Original Window'].unique() for df in sorted_data.values()])
    fig = go.Figure()

    # Iterate through windows
    for original_window in original_windows:
        # Iterate through sorted entity positions
        for entity_position, df in sorted_data.items():
            window_df = df[df['Original Window'] == original_window]
            if window_df.empty:
                continue
            # Get unique numeric positions
            unique_positions = sorted(window_df['Position'].unique())

            # Iterate through numeric target word positions
            for idx, target_word_position in enumerate(unique_positions):
                position_group_df = window_df[window_df['Position'] == target_word_position]
                if position_group_df.empty:
                    continue

                # Map target word position to a color from the color scale
                color = color_scale[idx % len(color_scale)]

                # Aggregate statistics
                stats = position_group_df.groupby('Hamming Distance').agg({
                    'Similarity': ['mean', 'std'],
                    'Euclidean Distance': ['mean', 'std']
                }).reset_index()
                stats.columns = ['Hamming Distance', 'Similarity Mean', 'Similarity Std', 'Euclidean Mean', 'Euclidean Std']

                # Add trace
                fig.add_trace(go.Scatter(
                    x=stats['Hamming Distance'],
                    y=stats['Similarity Mean'],
                    mode='lines+markers',
                    name=f"Target Word Position: {target_word_position}, Phrase Position: {entity_position}",
                    line=dict(color=color, dash=entity_styles[entity_position]),
                    marker=dict(size=10, color=color, opacity=0.6),
                    text=stats.apply(
                        lambda row: f"Original Window: {original_window}<br>"
                                    f"Hamming Distance: {row['Hamming Distance']}<br>"
                                    f"Similarity: {row['Similarity Mean']:.4f} ± {row['Similarity Std']:.4f}<br>"
                                    f"Euclidean Distance: {row['Euclidean Mean']:.4f} ± {row['Euclidean Std']:.4f}",
                        axis=1
                    ),
                    hoverinfo='text'
                ))

    # Configure layout
    fig.update_layout(
        title=f"Combined Cosine Similarity by Hamming Distance\nOriginal Window: '{original_window}' - RPP: {mode}",
        xaxis_title="Hamming Distance",
        yaxis_title="Mean Cosine Similarity",
        yaxis=dict(
            range=[0, 1],
            tickmode='array',
            tickvals=[i / 10 for i in range(11)],
            ticktext=[f"{i / 10:.1f}" for i in range(11)]
        ),
        template="plotly_white",
        hovermode='closest',
        legend=dict(x=1.1, y=1),
        margin=dict(r=150, t=100, b=50, l=50)
    )

    # Update trace and interactivity settings
    fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))
    fig.update_layout(clickmode='event+select')

    fig.show()
    return fig
