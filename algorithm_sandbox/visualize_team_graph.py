from dash import Dash, html, dcc, callback_context
from dash.dependencies import Input, Output
import visdcc

def vis(graph, logs):
    
    app = Dash(__name__)
    
    app.layout = html.Div([
    visdcc.Network(id = 'net', 
            options = dict(
                         height= '500px', 
                         width= '100%', 
                         edges= { 'arrows':{ 'to': {'enabled': True}}},
                         physics= { 'barnesHut': {'avoidOverlap': 0.5}},
                         interaction= {'hover': True},
                         )
                     ),
        html.Div([
        html.Div(id='iteration'),
        html.Button('Previous', id='btn_1'),
        html.Button('Next', id='btn_2'),
        ]),
        html.Div([
        "Display Edge information: ",
        dcc.Dropdown(['Display All', 'Friends Only', 'Enemy Only'], 'Display All', id='edge-dropdown'),
        ]),
        ])

    @app.callback(
        [Output('net', 'data'),
         Output('iteration', 'children')],
        [Input('btn_1', 'n_clicks'),
        Input('btn_2', 'n_clicks'),
        Input('edge-dropdown', 'value')])
    def init_graph(btn1,btn2,value):
        
        recent_clicked_button = [p['prop_id'] for p in callback_context.triggered][0]
        
        if 'btn_2' in recent_clicked_button:
            logs.next()
            print(logs.state())
        
        elif 'btn_1' in recent_clicked_button:
            logs.prev()
            print(logs.state())
        
        nodes = []
        edges = []
        
        app.logger.info(value)
        
        node = graph.get_nodes()
        edge = graph.get_edges()
        
        if logs.state() == 0:
            for n in node:
                nodes.append({
                    'id': n,
                    'label': str(n),
                    'color': 'rgb(97,195,238)',
                
                })
            for source, D_W in edge.items():
                for dest_and_weight in D_W:
                    destination = dest_and_weight[0]
                    weight = dest_and_weight[1]
                    if value == "Display All":
                        if weight == 1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'green'},
                    
                            })
                        elif weight == -1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'red'},

                        })
                
                    elif value == "Friends Only":
                        if weight == 1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'green'},
                    
                            }) 
                        
                    elif value == "Enemy Only":
                        if weight == -1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'red'},

                        })
                
        elif logs.state() > 0: 
            current_interation = logs.current_algorithm_states
            for n in node:   
                if any(n in sublist for sublist in current_interation):
                    nodes.append({
                        'id': n,
                        'label': n,
                        'color':'grey'
                
                    })
                else:
                    nodes.append({
                    'id': n,
                    'label': n,
                    'color': 'rgb(97,195,238)',
                
                    })
            
            for source, D_W in edge.items():
                for dest_and_weight in D_W:
                    destination = dest_and_weight[0]
                    weight = dest_and_weight[1]
                    if value == "Display All":
                        if weight == 1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'green'},
                    
                            })
                        elif weight == -1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'red'},

                        })
                
                    elif value == "Friends Only":
                        if weight == 1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'green'},
                    
                            }) 
                        
                    elif value == "Enemy Only":
                        if weight == -1:
                            edges.append({
                                'id':str(source) +"_"+str(destination),
                                'from':source,
                                'to':destination,
                                'color': {'color':'red'},

                        })
        
        data = {'nodes':nodes, 'edges': edges}
    
        
        log_iteration = f'Current Algorithm iteration: {logs.state()}'
        
        return data, log_iteration

    app.run_server(dev_tools_ui=True,
          dev_tools_hot_reload =True, threaded=True)
    