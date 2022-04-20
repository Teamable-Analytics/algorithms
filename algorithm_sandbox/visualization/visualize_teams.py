import visdcc
from dash import Dash, html, Output, Input, callback_context

from algorithm_sandbox.visualization.visualize_logs import VisualizeLogs
from team_formation.app.team_generator.algorithm.consts import UNREGISTERED_STUDENT_ID


def visualize_teams_network(visualize_logs: VisualizeLogs):
    app = Dash(__name__)
    app.layout = html.Div([
        visdcc.Network(id='net',
                       options=dict(
                           height='650px',
                           width='100%',
                           edges={'arrows': {'to': {'enabled': True}}},
                           physics={'barnesHut': {'avoidOverlap': 0.1}},
                           interaction={'hover': True}
                       )
                       ),
        html.Div([
            html.Div(id='iteration'),
            html.Button('Previous', id='prev_btn'),
            html.Button('Next', id='next_btn'),
        ]),
    ])

    @app.callback(
        [Output('net', 'data'), Output('iteration', 'children')],
        [Input('prev_btn', 'n_clicks'), Input('next_btn', 'n_clicks')]
    )
    def visualize_teams_in_graph(prev_btn, next_btn):
        def get_recent_button_click():
            return [p['prop_id'] for p in callback_context.triggered][0]

        def handle_button_click():
            recent_clicked_button = get_recent_button_click()
            if 'next_btn' in recent_clicked_button:
                visualize_logs.next()
            if 'prev_btn' in recent_clicked_button:
                visualize_logs.prev()

        handle_button_click()  # handle button click event
        for student in visualize_logs.all_students:
            for target_id, relationship_value in student.relationships.items():
                if target_id == UNREGISTERED_STUDENT_ID:
                    continue
                visualize_logs.draw_relationship_edge(student.id, target_id, relationship_value)

        data = {'nodes': visualize_logs.nodes, 'edges': visualize_logs.edges}
        log_iteration = f'Current Algorithm iteration: {visualize_logs.state_index}\n' \
                        f'Algorithm Stage: {visualize_logs.get_current_stage()}'
        return data, log_iteration

    app.run_server(dev_tools_ui=True, dev_tools_hot_reload=True, threaded=True)
