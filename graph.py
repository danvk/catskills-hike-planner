import networkx as nx


def get_index_for_type(features: list, type: str) -> dict[int, any]:
    type_features = [f for f in features if f['properties'].get('type') == type]
    return {f['properties']['id']: f for f in type_features}


def get_peak_index(features: list):
    return get_index_for_type(features, 'high-peak')


def get_lot_index(features: list):
    return get_index_for_type(features, 'parking-lot')


def get_trailhead_index(features: list):
    return get_index_for_type(features, 'trailhead')


def read_hiking_graph(
    features,
) -> tuple[nx.Graph, dict[int, any], dict[int, any], dict[int, any]]:
    id_to_peak = get_peak_index(features)

    G = nx.Graph()
    for f in features:
        if f['geometry']['type'] != 'LineString':
            continue
        nodes = f['properties']['nodes']
        for node in nodes[1:-1]:
            assert node not in id_to_peak  # and node not in id_to_lot
        a, b = nodes[0], nodes[-1]
        d_km = f['properties']['d_km']
        G.add_edge(a, b, weight=d_km, feature=f)

    for n in G.nodes():
        f = G.nodes[n].get('feature', {})
        p = f.get('properties', {})
        G.nodes[n]['type'] = p.get('type', 'junction')

    return G
