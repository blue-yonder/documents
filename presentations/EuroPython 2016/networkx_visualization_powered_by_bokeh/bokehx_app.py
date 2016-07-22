""""
This is the example bokeh app made for the EuroPython 2016 Talk.
It is derived from the jupyter notebook and extended by buttons and update functions.
Therefore this app does not represent the best coding example and parts could be done nicer.
"""
from bokeh.layouts import widgetbox, column, row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.models import HoverTool, Select, Button
import community # package name: python-louvain
from math import sqrt
import networkx
from networkx.algorithms import centrality as centrality_algorithms

network = networkx.read_gml('ep2016.gml')
# https://github.com/gephi/gephi/wiki/Datasets

layout = networkx.spring_layout(network, k=1.1/sqrt(network.number_of_nodes()), iterations=100)
# https://en.wikipedia.org/wiki/Force-directed_graph_drawing

nodes, nodes_coordinates = zip(*sorted(layout.items()))
nodes_xs, nodes_ys = list(zip(*nodes_coordinates))
nodes_source = ColumnDataSource(dict(x=nodes_xs, y=nodes_ys, name=nodes))

hover = HoverTool(tooltips=[('name', '@name'), ('id', '$index')])
plot = figure(plot_width=800, plot_height=400, tools=['tap', hover, 'reset', 'box_zoom'])
r_circles = plot.circle('x', 'y', source=nodes_source, size=10, color='blue', level='overlay')


def get_edges_specs(_network, _layout):
    d = dict(xs=[], ys=[], alphas=[])
    weights = [d['weight'] for u, v, d in _network.edges(data=True)]
    max_weight = max(weights)
    calc_alpha = lambda h: 0.1 + 0.6 * (h / max_weight)

    # example: { ..., ('user47', 'da_bjoerni', {'weight': 3}), ... }
    for u, v, data in _network.edges(data=True):
        d['xs'].append([_layout[u][0], _layout[v][0]])
        d['ys'].append([_layout[u][1], _layout[v][1]])
        d['alphas'].append(calc_alpha(data['weight']))
    return d


lines_source = ColumnDataSource(get_edges_specs(network, layout))
r_lines = plot.multi_line('xs', 'ys', line_width=1.5, alpha='alphas', color='navy',
                          source=lines_source)

centrality = networkx.algorithms.centrality.degree_centrality(network)
# first element, are nodes again
_, nodes_centrality = zip(*sorted(centrality.items()))
nodes_source.add([7 + 10 * t / max(nodes_centrality) for t in nodes_centrality], 'centrality')

partition = community.best_partition(network)
p_, nodes_community = zip(*sorted(partition.items()))
nodes_source.add(nodes_community, 'community')
community_colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628', '#b3cde3','#ccebc5','#decbe4','#fed9a6','#ffffcc','#e5d8bd','#fddaec','#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#e6ab02','#a6761d','#666666']
nodes_source.add([community_colors[t % len(community_colors)]
                  for t in nodes_community], 'community_color')

r_circles.glyph.size = 'centrality'
r_circles.glyph.fill_color = 'community_color'


def remove_node():
    idx = nodes_source.selected['1d']['indices'][0]

    # update networkX network object
    node = nodes_source.data['name'][idx]
    network.remove_node(node)

    # update layout
    layout.pop(node)

    # update nodes ColumnDataSource
    new_source_data = dict()
    for column in nodes_source.column_names:
        new_source_data[column] = [e for i, e in enumerate(nodes_source.data[column]) if i != idx]
    nodes_source.data = new_source_data

    # update lines ColumnDataSource
    lines_source.data = get_edges_specs(network, layout)


drop_button = Button(label="Remove Node")
drop_button.on_click(remove_node)


def remove_unbound_nodes():
    unbound_nodes = []
    for node in network.nodes_iter():
        if not network.edges(node):
            unbound_nodes.append(node)
    for node in unbound_nodes:
        network.remove_node(node)
        layout.pop(node)

    nodes, nodes_coordinates = zip(*sorted(layout.items()))
    nodes_xs, nodes_ys = list(zip(*nodes_coordinates))
    nodes_source.data = dict(x=nodes_xs, y=nodes_ys, name=nodes,
                             community_color=[], community=[], centrality=[])
    update_properties()
    lines_source.data = get_edges_specs(network, layout)


remove_unattached_button = Button(label="Remove unattached nodes")
remove_unattached_button.on_click(remove_unbound_nodes)


def update_properties():
    partition = community.best_partition(network)
    p_, nodes_community = zip(*sorted(partition.items()))
    nodes_source.data['community'] = nodes_community
    nodes_source.data['community_color'] = [community_colors[t % len(community_colors)]
                                            for t in nodes_community]
    centrality = centrality_metrics[select_centrality.value](network, weight='weight')
    _, nodes_centrality = zip(*sorted(centrality.items()))
    nodes_source.data['centrality'] = [7 + 10 * t / max(nodes_centrality) for t in nodes_centrality]


update_props_button = Button(label="Update Properties")
update_props_button.on_click(update_properties)

centrality_metrics = {"Degree Centrality":
                          lambda n, weight=_: centrality_algorithms.degree_centrality(n),
                      "Closeness Centrality":
                          lambda n, weight=_: centrality_algorithms.closeness_centrality(n),
                      "Betweenness Centrality":
                          centrality_algorithms.betweenness_centrality}


def update_centrality(attrname, old, new):
    centrality = centrality_metrics[select_centrality.value](network, weight='weight')
    _, nodes_centrality = zip(*sorted(centrality.items()))
    nodes_source.data['centrality'] = [7 + 10 * t / max(nodes_centrality) for t in nodes_centrality]


select_centrality = Select(title="Centrality Metric:", value="Degree Centrality",
                           options=list(centrality_metrics.keys()))
select_centrality.on_change('value', update_centrality)


def update_layout():
    global layout
    new_layout = networkx.spring_layout(network, k=1.1/sqrt(network.number_of_nodes()),
                                        iterations=100)
    layout = new_layout
    nodes, nodes_coordinates = zip(*sorted(layout.items()))
    nodes_xs, nodes_ys = list(zip(*nodes_coordinates))
    nodes_source.data['x'] = nodes_xs
    nodes_source.data['y'] = nodes_ys
    lines_source.data = get_edges_specs(network, layout)


update_layout_button = Button(label="Update Layout")
update_layout_button.on_click(update_layout)


inputs = row(select_centrality, widgetbox(drop_button, update_props_button, update_layout_button,
                                          remove_unattached_button))

curdoc().add_root(column(plot, inputs))
