"""I need to hike a set of peaks. What are my options?

Sample invocation:

    poetry run python peak_planner.py H,BD,TC,C,Pl,Su,W,SW,KHP,Tw,IH,WHP
"""

import json

from subset_cover import find_optimal_hikes_subset_cover



MODES = [
    'unrestricted',
    'loops-only',
    'day-only',
    'day-loop-only',
    'prefer-loop',
    'day-only-prefer-loop',
]

def plan_hikes(peaks_to_hike: list[str], mode: str = 'unrestricted'):
    features = json.load(open('data/network+parking.geojson'))['features']
    all_hikes: list[tuple[float, float, list[int]]] = json.load(open('data/hikes.json'))

    PEAKS = [
        (f['properties']['code'], f['properties']['id'], f['properties']['name'])
        for f in features
        if f['properties'].get('type') == 'high-peak'
    ]

    ha_code_to_osm_id = {ha_code: osm_id for ha_code, osm_id, _name in PEAKS}
    osm_ids = [ha_code_to_osm_id[ha_code] for ha_code in peaks_to_hike]
    assert mode in MODES

    osm_ids_set = set(osm_ids)
    relevant_hikes = [
        h for h in all_hikes if any(peak_id in osm_ids_set for peak_id in h[-1])
    ]

    if mode == 'unrestricted':
        hikes = relevant_hikes
    elif mode == 'loops-only':
        hikes = [
            (d, ele, nodes) for d, ele, nodes in relevant_hikes if nodes[0] == nodes[-1]
        ]
    elif mode == 'day-only':
        # TODO: parameterize the 21km
        hikes = [
            (d, ele, nodes) for d, ele, nodes in relevant_hikes if d < 21
        ]  # 21km = ~13 miles
    elif mode == 'day-loop-only':
        hikes = [
            (d, ele, nodes)
            for d, ele, nodes in relevant_hikes
            if d < 21 and nodes[0] == nodes[-1]
        ]
    elif mode == 'prefer-loop':
        # TODO: parameterize the 3.5km penalty
        hikes = [
            (d + (0 if nodes[0] == nodes[-1] else 3.5), ele, nodes, d)
            for d, ele, nodes in relevant_hikes
        ]
    elif mode == 'day-only-prefer-loop':
        hikes = [
           (d + (0 if nodes[0] == nodes[-1] else 3.5), ele, nodes, d)
            for d, ele, nodes in relevant_hikes if d < 21
        ]
    else:
        raise ValueError(mode)

    out = {
        'peaks_to_hike': peaks_to_hike,
        'peak_ids': PEAKS,
        'hikes_considered': len(hikes),
    }

    d_km, chosen, fc = find_optimal_hikes_subset_cover(features, hikes, osm_ids)
    out['solution'] = {
        'd_km': d_km,
        'd_mi': d_km * 0.621371,
        'num_hikes': len(chosen),
        'hikes': chosen,
        'features': fc['features'],
    }

    return out
