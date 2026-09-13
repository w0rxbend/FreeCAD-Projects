"""Independent checks of generated triangle meshes."""

import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from math import isfinite
from pathlib import Path
from zipfile import ZipFile


def audit_mesh(vertices: list[tuple], triangles: list[tuple]) -> dict:
    if not all(isfinite(value) for vertex in vertices for value in vertex):
        raise ValueError("Mesh contains a non-finite coordinate")
    unique = {point: i for i, point in enumerate(dict.fromkeys(vertices))}
    indices = [unique[point] for point in vertices]
    edges: Counter = Counter()
    directions: Counter = Counter()
    neighbors: dict[int, set[int]] = defaultdict(set)
    degenerate = 0
    for triangle in triangles:
        if any(i < 0 or i >= len(vertices) for i in triangle):
            raise ValueError("Mesh contains an invalid vertex index")
        a, b, c = (vertices[i] for i in triangle)
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        degenerate += sum(value * value for value in normal) < 1e-20
        ids = [indices[i] for i in triangle]
        for start, end in zip(ids, ids[1:] + ids[:1], strict=True):
            edges[tuple(sorted((start, end)))] += 1
            directions[start, end] += 1
            neighbors[start].add(end)
            neighbors[end].add(start)
    remaining = set(neighbors)
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            for neighbor in neighbors[stack.pop()]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    boundary = sum(count == 1 for count in edges.values())
    nonmanifold = sum(count > 2 for count in edges.values())
    winding = sum(directions[a, b] != directions[b, a] for a, b in edges)
    return {
        "valid": bool(triangles)
        and components == 1
        and not any((degenerate, boundary, nonmanifold, winding)),
        "triangles": len(triangles),
        "components": components,
        "degenerate_faces": degenerate,
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "winding_errors": winding,
    }


def audit_3mf(path: Path) -> dict:
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
    meshes = root.findall(".//{*}mesh")
    if len(meshes) != 1 or root.get("unit") != "millimeter":
        raise ValueError("A component 3MF must contain one mesh in millimeters")
    vertices = [
        tuple(float(v.attrib[axis]) for axis in "xyz")
        for v in meshes[0].findall("./{*}vertices/{*}vertex")
    ]
    triangles = [
        tuple(int(t.attrib[axis]) for axis in ("v1", "v2", "v3"))
        for t in meshes[0].findall("./{*}triangles/{*}triangle")
    ]
    report = audit_mesh(vertices, triangles)
    if not report["valid"]:
        raise ValueError(f"Invalid component mesh in {path}: {report}")
    return report
