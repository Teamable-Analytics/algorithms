# Visualization

Visualization section is used to visualize the student relationship graph that is passed in by the social algorithm. it uses Dash python framework and visdcc library to render social algorithm in browser

## Installation

Graph Visualization does not require special tool 

Install the required libraries from requirement.txt

```sh
pip install -r requirements.txt
```

For demonstration and testing purposes run following file in the root directory

```sh
python vis_test.py
```
and go to http://127.0.0.1:8050 in any modern browser

## Features
### Graph
- A graph with all student as nodes and all their relationship as edges
- Student node display student ID
- Distinguish relationship edges with green(as friend) and red(as enemy)
- On hover over any node with mouse cursor all connected edges with the student node will be hightlighted
- Iteration control button:
  - Two bottons(Next and Previous) that display team with in different itertion of the the social algorithm
  - Indication right above the button that show which Current Algorithm iteration the graph is currently on and which Algorithm Stage the graph is currently on
- Edge Dropdown Table:
  - Dynamically toggle edge display with a dropdown table
  - Consist of three options: Display all(display all edges), Friends only(display edges with friend relationship), Enemies only(display edges with enemy relationship)

## Important Classes and Functions 
 - VisualizeLogs is a class that stores the esstential information that visualization function to generate the graph, located in `visualize_logs.py`
 - visualize_teams_network is the visualization function that takes VisualizeLogs class object as input to generate and render the social algorithm graph, located in `visualize_teams.py`. 

## Input Data
The Visulaztion function takes in a VisualizeLogs object which is initialized by a logger object which are normally generated after social algorithm was executed.

## Expected output
After given visualize_teams_network function correct input and executed the function, go to http://127.0.0.1:8050 in the brower and the graph will be rendered.

## Folder Structure

📂visualization  

┣ 📜init.py  
┣ 📜visualize_logs.py  
┗ 📜visualize_teams.py  
 
 ### `init.py`
 This python file is to load functions from `visualize_logs.py` and `visualize_teams.py` to root directory entry file.
 
 ### `visualize_logs.py`
 - Class VisualizeLogs
    - init
        - Takes logger class as input
        - algorithm_states: this is a list store all stage and iteration infromation of the social algorithm
        - nodes: This is a list of dictionary that store information of all node
        - edges: This is a list of dictionary that store information of all edges
        - _nodes_cache, _student_cache: prevent repeat
        - logger: store input logger
        - state_index: which iteration and stage the graph is current on
    - next: increment state_index by 1
    - prev: decrement state_index by 1
    - get_student_by_id: return student based on input student ID
    - get_current_team_compositions: return team compositions at current algorithm state
    - get_current_stage: return current stage of the algorithm
    - student_currently_in_team: return all the student that is current in a team
    - state: return state_index
    - draw_student_node: append a dictionary that contain the student node information to the nodes list
    - get_node_colour: return node colour for draw_student_node function
    - draw_student_edge: append a dictionary that contain the realtionship edge information to the edges list
    - get_edge_colour: return colur for edges based on the relationship
    - draw_relationship_edge: this function calls all draw functions
    - reset: remove all exist node and edge stored in nodes list, edges list, and _nodes_cache
 
 ### `visualize_teams.py`
 - Take VisualizeLogs object as input
 - app.layout
    - visdcc.Network: indicate all setting for the rendered graph 
    - HTML,dcc: HTML component that service the graph
 - @app.callback: indicate all outputs and inputs
 - visualize_teams_in_graph:
    - get_recent_button_click: return which button was clicked
    - handle_button_click: this function triggers next() and prev() function in VisualizeLogs class in order to change the current stage and iteration that is showed in graph
    - a for loop that loop through all studentd and stores all information about student nodes and relationship edges in a dictionary called "data" for Dash to render in browser
 -  app.run_server: indicate Dash framework app is run in development