# utils/data_utils.py

import streamlit as st
import streamlit.components.v1 as components
from utils.api_client import get_genres, get_authors, get_books, get_recommendations, get_genre_metadata_from_api, get_genre_connections_from_api
import logging
import requests

import tempfile
import os
import pandas as pd
import json

logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_books():
    """
    Get all unique books from the API.
    Falls back to hardcoded values if API call fails.
    Also updates the session state with book metadata if available.
    """
    books = get_books()

    if books and isinstance(books, dict):
        book_list = books.get("books", [])
        metadata_list = books.get("metadata", [])

        # Ensure metadata cache is initialized
        if "book_metadata" not in st.session_state:
            st.session_state.book_metadata = {}

        for book in metadata_list:
            title = book.get("title", "").strip()
            author = book.get("author", "").strip()
            genre = book.get("genre", "Unknown Genre").strip()

            metadata = {
                "title": title,
                "author": author,
                "genre": genre
            }

            # Cache with plain title
            st.session_state.book_metadata[title] = metadata

            # Cache with display format
            display_key = f"{title} - {author}"
            st.session_state.book_metadata[display_key] = metadata

        return book_list

    # Fallback if API call fails or structure is unexpected
    return [
        "To Kill a Mockingbird - Harper Lee",
        "1984 - George Orwell",
        "Pride and Prejudice - Jane Austen",
        "The Great Gatsby - F. Scott Fitzgerald",
        "Moby Dick - Herman Melville"
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_genres():
    """
    Get all unique genres from the API.
    Falls back to hardcoded values if API call fails.
    """
    genres = get_genres()
    if not genres:
        # Fallback to hardcoded genres if API call fails
        return [
            "Fiction", "Non-Fiction", "Mystery", "Fantasy",
            "Science Fiction", "Romance", "History"
        ]
    return genres

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_authors():
    """
    Get all unique authors from the API.
    Falls back to hardcoded values if API call fails.
    """
    authors = get_authors()
    if not authors:
        # Fallback to hardcoded authors if API call fails
        return [
            "J.K. Rowling", "Stephen King", "Jane Austen",
            "Agatha Christie", "Neil Gaiman", "George R.R. Martin"
        ]
    return authors


@st.cache_data(ttl=3600)
def load_chord_viz_data():
    """Load genre metadata and connections for chord visualization from API"""
    
    genre_metadata = get_genre_metadata_from_api()
    genre_connections = get_genre_connections_from_api()
        
    # Check if we got valid data
    if genre_metadata.empty or genre_connections.empty:
        raise ValueError("Failed to retrieve visualization data from API")
        
    return genre_metadata, genre_connections
    

def prepare_chord_data(genre_metadata, genre_connections, top_n_genres=30, top_n_connections=100, user_genres=None):
    """
    Prepare data for D3.js chord diagram with user preferences highlighted.
    
    Parameters:
    -----------
    genre_metadata : DataFrame
        DataFrame containing genre metadata
    genre_connections : DataFrame
        DataFrame containing connections between genres
    top_n_genres : int, default=30
        Number of top genres to include by Genre Rank
    top_n_connections : int, default=100
        Number of top connections to include
    user_genres : list, default=None
        List of genres selected by the user
        
    Returns:
    --------
    dict: Processed data ready for D3 visualization
    """
    try:
        # Select top genres by Genre Rank instead of segment width
        top_genres = genre_metadata[genre_metadata['Genre Rank'] <= top_n_genres].copy()
        top_genre_ids = set(top_genres['Genre ID'].tolist())
        
        # Create ID to name mapping
        id_to_name = dict(zip(top_genres['Genre ID'], top_genres['Genre Name']))
        
        # Get genre names in order
        genre_names = [id_to_name[id] for id in top_genres['Genre ID']]
        
        # Filter connections to only include top genres
        filtered_connections = genre_connections[
            (genre_connections['Source Genre ID'].isin(top_genre_ids)) & 
            (genre_connections['Target Genre ID'].isin(top_genre_ids))
        ]
        
        # Get strongest connections
        strongest_connections = filtered_connections.nlargest(top_n_connections, 'Connection Strength')
        
        # Create a map of genres to their parent categories for coloring
        genre_to_parent = dict(zip(top_genres['Genre Name'], top_genres['Parent Category']))
        
        # Create list of unique parent categories for color assignment
        unique_parents = list(set(genre_to_parent.values()))
        
        # Check if user has selected any genres
        user_selected = []
        if user_genres:
            user_selected = [genre for genre in genre_names if genre in user_genres]
        
        # Build the final data structure
        chord_data = {
            "genres": genre_names,
            "parents": [genre_to_parent.get(genre, "Other") for genre in genre_names],
            "parentCategories": unique_parents,
            "userSelected": user_selected,
            "connections": [
                {
                    "source": id_to_name[row["Source Genre ID"]],
                    "target": id_to_name[row["Target Genre ID"]],
                    "weight": float(row["Connection Strength"]),
                    "isTopConnection": bool(row["Is Top Connection"])
                } for _, row in strongest_connections.iterrows()
            ]
        }
        
        return chord_data
        
    except Exception as e:
        logging.error(f"Error preparing chord data: {str(e)}")
        return {"error": str(e)}

def create_genre_chord_diagram(genre_metadata, genre_connections, top_n_genres=30, top_n_connections=100, user_genres=None):
    """
    Create an interactive D3.js chord diagram from genre data.
    
    Returns:
    --------
    str: HTML content for the chord diagram
    """
    try:
        # Prepare data
        chord_data = prepare_chord_data(
            genre_metadata, 
            genre_connections, 
            top_n_genres, 
            top_n_connections,
            user_genres
        )
        
        # If there was an error processing the data
        if "error" in chord_data:
            return f"<div style='color:red'>Error creating visualization: {chord_data['error']}</div>"
        
        # Convert data to JSON for JavaScript
        chord_json_str = json.dumps(chord_data)
        
        # D3.js Chord Diagram HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v6.min.js"></script>
            <style>
                body { 
                    font-family: 'Libre Baskerville', serif;
                    margin: 0;
                    padding: 0;
                    background-color: #E6E3DC;
                }

                .chord path {
                    fill-opacity: 0.75;
                    transition: opacity 0.3s;
                    stroke-width: 0.5px;
                }

                .chord.fade { 
                    opacity: 0.1; 
                }
                .group path {
                    transition: opacity 0.3s;
                }
                .group.highlighted path {
                    stroke-width: 2px;
                }
                .group.fade path {
                    opacity: 0.3;
                }
                .group.user-selected path {
                    stroke: #000000 !important;
                    stroke-width: 3px !important;
                }
                #tooltip {
                    position: absolute;
                    background-color: #4e7694;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    pointer-events: none;
                    font-size: 14px;
                    opacity: 0;
                    z-index: 100;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    transition: opacity 0.2s;
                }
                .controls {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: white;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                }
                button {
                    background: #4e7694;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-family: 'Libre Baskerville', serif;
                    font-size: 14px;
                    margin-right: 5px;
                }
                button:hover {
                    background: #3c5a75;
                }

                .controls {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: transparent; 
                    padding: 8px;
                    border: none;          
                }

                .legend {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(255,255,255,0.8);
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    max-width: 200px;
                }
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 3px;
                }
                .legend-color {
                    width: 15px;
                    height: 15px;
                    margin-right: 8px;
                    border-radius: 2px;
                }
                .legend-label {
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
        <div id="chart"></div>
        <div id="tooltip"></div>
        <div class="controls">
            <button id="highlightUserGenresButton">Highlight My Genres</button>
        </div>
        <script>
        // The chord data from Python
        const chordData = CHORD_DATA_PLACEHOLDER;
        
        // Extract data components
        const genres = chordData.genres;
        const parents = chordData.parents;
        const parentCategories = chordData.parentCategories;
        const connections = chordData.connections;
        const userSelected = chordData.userSelected || [];

        // Track the state
        let userGenresHighlighted = true;
        
        // Create the matrix for chord layout
        const matrix = Array(genres.length).fill(null).map(() => Array(genres.length).fill(0));
        
        // Populate the matrix
        connections.forEach(d => {
            const sourceIndex = genres.indexOf(d.source);
            const targetIndex = genres.indexOf(d.target);
            if (sourceIndex !== -1 && targetIndex !== -1) {
                matrix[sourceIndex][targetIndex] = d.weight;
            }
        });
        
        // Set up dimensions
        const width = 750, height = 750;
        const outerRadius = Math.min(width, height) * 0.42 - 60;
        const innerRadius = outerRadius - 30;
        
        // Create chord layout
        const chord = d3.chord()
            .padAngle(0.05)
            .sortSubgroups(d3.descending)
            (matrix);
        
        // Create arc and ribbon generators
        const arc = d3.arc()
            .innerRadius(innerRadius)
            .outerRadius(outerRadius);
            
        const ribbon = d3.ribbon()
            .radius(innerRadius);
        

        // Define fixed colors for each parent category
        const categoryColorMap = {
            "Fiction": "#1B5162", // Blue
            "Biography & Autobiography": "#8BCAE7", // Light Blue
            "Business & Economics": "#99DDB4", // Light Green
            "Religion": "#00A972", // Green 
            "Juvenile Fiction": "#BF7080" // Light Maroon 
        };

        // Create color scale based on parent categories, with explicit mappings
        const colorScale = d3.scaleOrdinal()
            .domain(parentCategories)
            .unknown("#919191") // Grey as default fallback
            .range(parentCategories.map(category => 
                // Use the explicit mapping if available, otherwise use gray
                categoryColorMap[category] || "#919191" // Grey as fallback
            ));
            
        // Create SVG
        const svg = d3.select("#chart").append("svg")
            .attr("viewBox", [-width / 2, -height / 2, width, height])
            .attr("width", "100%")
            .attr("height", "100%");
            
        // Create group for labels
        const labelsGroup = svg.append("g")
            .attr("class", "labels");
            
        // Flag for showing/hiding labels
        let showLabels = true;
            
        // Add groups (genre arcs)
        const groups = svg.append("g")
            .selectAll("g.group")
            .data(chord.groups)
            .join("g")
            .attr("class", d => {
                const genreName = genres[d.index];
                return "group" + 
                       (userSelected.includes(genreName) ? " user-selected" : "");
            });
            
        // Add paths for arcs
        groups.append("path")
            .attr("fill", d => colorScale(parents[d.index]))
            .attr("stroke", "white")
            .attr("d", arc)
            .on("mouseover", (event, d) => handleGroupHover(d.index))
            .on("mouseout", resetHighlighting)
            .on("click", (event, d) => focusOnGenre(d.index));
            
        // Add chord connections
        const chords = svg.append("g")
            .attr("class", "chords")
            .selectAll(".chord")
            .data(chord)
            .join("path")
            .attr("class", "chord")
            .attr("d", ribbon)
            .attr("fill", d => colorScale(parents[d.source.index]))
            .attr("stroke", "white")
            .attr("stroke-width", 0.5)
            .on("mouseover", handleChordHover)
            .on("mouseout", resetHighlighting);
            
        // Add labels
        const labels = labelsGroup.selectAll("text")
            .data(chord.groups)
            .join("text")
            .attr("dy", ".35em")
            .attr("text-anchor", d => (d.startAngle + d.endAngle) / 2 > Math.PI ? "end" : "start")
            .attr("transform", d => {
                const angle = (d.startAngle + d.endAngle) / 2;
                const labelRadius = outerRadius + 10;
                const x = labelRadius * Math.cos(angle - Math.PI / 2);
                const y = labelRadius * Math.sin(angle - Math.PI / 2);
                const rotation = angle * 180 / Math.PI - 90;
                return `translate(${x},${y}) rotate(${(d.startAngle + d.endAngle) / 2 > Math.PI ? rotation + 180 : rotation})`;
            })
            .text(d => genres[d.index])
            .style("font-size", "11px")
            .style("fill", "#333");
            
        // Create tooltip
        const tooltip = d3.select("#tooltip");
        
        // Functions for interactivity
        function handleGroupHover(index) {
            // Only show tooltip regardless of highlighting state
            tooltip
                .style("opacity", 1)
                .html(`<strong>${genres[index]}</strong><br>${parents[index]}`)
                .style("left", (d3.event ? d3.event.pageX : window.event.pageX) + 10 + "px")
                .style("top", (d3.event ? d3.event.pageY : window.event.pageY) - 25 + "px");
            
            // Only apply hover highlighting effects if user genres are not highlighted
            if (!userGenresHighlighted) {
                // Highlight relevant chords and fade others
                chords.classed("fade", d => d.source.index !== index && d.target.index !== index);
                
                // Highlight the hovered group
                groups.classed("highlighted", d => d.index === index);
                groups.classed("fade", d => d.index !== index);
            }
        }
                
        function handleChordHover(event, d) {
            // Calculate values for tooltip
            const sourceGenre = genres[d.source.index];
            const targetGenre = genres[d.target.index];
            const value = d.source.value.toFixed(2);
            
            // Position and show tooltip
            tooltip
                .style("opacity", 1)
                .html(`
                    <strong>${sourceGenre}</strong> → <strong>${targetGenre}</strong><br>
                    <span style="font-size: 12px;">Readers who enjoy ${sourceGenre} 
                    often read ${targetGenre} as well</span><br>
                    <span style="font-size: 13px;">Connection Strength: ${(value * 100).toFixed(0)}%</span>
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 25) + "px");
                
            // Only apply highlighting if user genres are not highlighted
            if (!userGenresHighlighted) {
                // Highlight just this chord
                chords.classed("fade", p => p !== d);
                
                // Highlight relevant groups
                groups.classed("highlighted", p => p.index === d.source.index || p.index === d.target.index);
                groups.classed("fade", p => p.index !== d.source.index && p.index !== d.target.index);
            }
        }
        
        function resetHighlighting() {
            tooltip.style("opacity", 0);
            chords.classed("fade", false);
            groups.classed("fade", false);
            groups.classed("highlighted", false);
            
            // Reset the user genres highlighting state if it was active
            if (userGenresHighlighted) {
                userGenresHighlighted = false;
                d3.select("#highlightUserGenresButton").text("Highlight My Genres");
            }
        }
                
        function focusOnGenre(index) {
            // First reset any existing highlighting
            resetHighlighting();
            
            // Then apply new highlighting - only show connections to/from this genre
            chords.style("display", d => (d.source.index === index || d.target.index === index) ? "block" : "none");
            
            // Highlight the selected genre and fade others
            groups.classed("fade", d => d.index !== index && 
                !chord.some(c => (c.source.index === index && c.target.index === d.index) || 
                                (c.source.index === d.index && c.target.index === index)));
        }
        
        function toggleUserGenresHighlight() {
            // Toggle the state
            userGenresHighlighted = !userGenresHighlighted;
            
            if (userGenresHighlighted) {
                // Get indices of user's genres
                const userGenreIndices = userSelected.map(genre => genres.indexOf(genre))
                                    .filter(index => index !== -1);
                
                // Highlight chords connected to user's genres
                chords.classed("fade", d => {
                    // Check if either source or target is in user's genres
                    const sourceInUserGenres = userGenreIndices.includes(d.source.index);
                    const targetInUserGenres = userGenreIndices.includes(d.target.index);
                    return !(sourceInUserGenres || targetInUserGenres);
                });
                
                // Highlight the groups
                groups.classed("fade", d => !userGenreIndices.includes(d.index));
                groups.classed("highlighted", d => userGenreIndices.includes(d.index));
                
                // Change button text
                d3.select("#highlightUserGenresButton").text("Show All Genre Connections");
            } else {
                // Reset highlighting
                resetHighlighting();
                
                // Reset button text
                d3.select("#highlightUserGenresButton").text("Highlight My Genres");
            }
        }

        // Add event listener for the highlight user genres button
        d3.select("#highlightUserGenresButton").on("click", toggleUserGenresHighlight);
        
        // Apply user genre highlighting on page load
        (function applyInitialHighlighting() {
            // Get indices of user's genres
            const userGenreIndices = userSelected.map(genre => genres.indexOf(genre))
                                    .filter(index => index !== -1);
            
            // Only apply highlighting if there are any user genres to highlight
            if (userGenreIndices.length > 0) {
                // Highlight chords connected to user's genres
                chords.classed("fade", d => {
                    // Check if either source or target is in user's genres
                    const sourceInUserGenres = userGenreIndices.includes(d.source.index);
                    const targetInUserGenres = userGenreIndices.includes(d.target.index);
                    return !(sourceInUserGenres || targetInUserGenres);
                });
                
                // Highlight the groups
                groups.classed("fade", d => !userGenreIndices.includes(d.index));
                groups.classed("highlighted", d => userGenreIndices.includes(d.index));
                
                // Set the button text to match the state
                d3.select("#highlightUserGenresButton").text("Show All Genre Connections");
            }
        })();

        </script>
        </body>
        </html>
        """
        
        # Insert the data into the template
        html_content = html_template.replace("CHORD_DATA_PLACEHOLDER", chord_json_str)
        
        return html_content
        
    except Exception as e:
        logging.error(f"Error creating chord diagram: {str(e)}")
        return f"""
        <div style="padding: 20px; background-color: #fee; border-left: 5px solid #f44; border-radius: 4px;">
            <h3>Error Creating Visualization</h3>
            <p>{str(e)}</p>
        </div>
        """

