"""I need to hike a set of peaks. What are my options?

Sample invocation:

    poetry run python peak_planner.py H,BD,TC,C,Pl,Su,W,SW,KHP,Tw,IH,WHP
"""

from dataclasses import dataclass
import json

from subset_cover import find_optimal_hikes_subset_cover



MODES = [
    'unrestricted',
    'loops-only',
    'prefer-loop',
]

@dataclass
class Area:
    name: str
    maxiters: int


AREAS = {
    'adk': Area(name='Adirondacks', maxiters=2),
    'catskills': Area(name='Catskills', maxiters=8),
}

# TODO: parameterize the 3.5km penalty
NON_LOOP_PENALTY_KM = 3.5

def plan_hikes(
    area: str,
    peaks_to_hike: list[str],
    mode: str = 'unrestricted',
    max_len_km: float = 1_000
):
    area_spec = AREAS[area]
    features = json.load(open(f'data/{area}/network.geojson'))['features']
    all_hikes: list[tuple[float, float, list[int]]] = json.load(open(f'data/{area}/hikes.json'))

    peaks = [
        (f['properties']['code'], f['properties']['id'], f['properties']['name'])
        for f in features
        if f['properties'].get('type') == 'high-peak'
    ]

    ha_code_to_osm_id = {ha_code: osm_id for ha_code, osm_id, _name in peaks}
    osm_ids = [ha_code_to_osm_id[ha_code] for ha_code in peaks_to_hike]
    assert mode in MODES

    osm_ids_set = set(osm_ids)
    relevant_hikes = [
        h for h in all_hikes if any(peak_id in osm_ids_set for peak_id in h[-1])
    ]
    print(f'{osm_ids_set=}, {len(osm_ids_set)}, {len(osm_ids)}, {peaks_to_hike=}')

    hikes = [h for h in relevant_hikes if h[0] <= max_len_km]

    if mode == 'loops-only':
        hikes = [(d, ele, nodes) for d, ele, nodes in hikes if nodes[0] == nodes[-1]]
    elif mode == 'prefer-loop':
        hikes = [
            (d + (0 if nodes[0] == nodes[-1] else NON_LOOP_PENALTY_KM), ele, nodes, d)
            for d, ele, nodes in hikes
        ]
        raise ValueError(mode)

    # Always include the shortest loop to each peak, regardless of constraints
    peak_to_shortest = {}
    for hike in relevant_hikes:
        nodes = hike[-1]
        if nodes[0] != nodes[-1]:
            continue
        for node in nodes[1:-1]:
            old = peak_to_shortest.get(node)
            if not old or old[0] > hike[0]:
                peak_to_shortest[node] = hike
    hikes += [*peak_to_shortest.values()]

    print(f'Considering {len(hikes)} hikes')
    out = {
        'peaks_to_hike': peaks_to_hike,
        'peak_ids': peaks,
        'hikes_considered': len(hikes),
    }
    # print(hikes)

    d_km, chosen, fc = find_optimal_hikes_subset_cover(features, hikes, osm_ids, maxiters=area_spec.maxiters)
    out['solution'] = {
        'd_km': d_km,
        'd_mi': d_km * 0.621371,
        # TODO: add total elevation gain
        'num_hikes': len(chosen),
        'hikes': chosen,
        'features': fc['features'],
    }

    return out
