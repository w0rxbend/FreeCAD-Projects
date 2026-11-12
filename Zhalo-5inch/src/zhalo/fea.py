"""Finite-element check of the arm (optional: needs the `fea` extra, gmsh and scikit-fem).

The arm's real 3D shape is meshed with quadratic tetrahedra and solved as a linear,
orthotropic solid: a woven 0/90 plate with its fibres along and across the arm. The part of
the arm that the two plates cover is held on both faces; the load goes into the walls of
the four motor screw holes.

Two static cases, 1 N each (the model is linear, so everything scales):
  vertical  - force along Z at the motor
  side      - force across the arm, in its own plane

and the first natural frequencies with the motor's mass on the pad.

What to trust: displacements, stiffness and frequencies converge quickly and are good. Peak
stress at the very edge of the clamp is a singularity of the idealised rigid clamp, so the
reported stress is the level exceeded by only 0.5 % of the arm's free volume, and it is the
comparison between two arms on the same mesh size that carries weight, not the absolute number.
"""

import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from zhalo import frame as F
from zhalo import params as P
from zhalo.structure import MATERIAL, Material

MESH_SIZE = 1.6  # mm; three quadratic elements through a 5-6 mm arm
TIP_MASS = 40.0  # g: motor, prop, screws


@dataclass
class Case:
    stiffness: float  # N/mm at the motor
    stress: float  # MPa per newton along the fibres, 99.5th percentile over the free part
    shear: float  # MPa per newton interlaminar shear, same percentile
    load: float  # N at which either allowable is reached
    governs: str  # which allowable that is
    where: float  # station u of the most stressed region, mm from the stack bolt


@dataclass
class Report:
    design: str
    thickness: float
    free_length: float
    mass: float  # g, whole arm
    nodes: int
    elements: int
    vertical: Case
    side: Case
    frequencies: list[float]  # Hz, first four

    def as_dict(self) -> dict:
        return asdict(self)


def _stiffness_matrix(m: Material) -> np.ndarray:
    """6 x 6 elastic matrix in Voigt order 11, 22, 33, 23, 13, 12 (engineering shear strains)."""
    s = np.zeros((6, 6))
    e1 = e2 = m.e1
    s[0, 0], s[1, 1], s[2, 2] = 1 / e1, 1 / e2, 1 / m.e3
    s[0, 1] = s[1, 0] = -m.nu12 / e1
    s[0, 2] = s[2, 0] = s[1, 2] = s[2, 1] = -m.nu13 / e1
    s[3, 3] = s[4, 4] = 1 / m.g13
    s[5, 5] = 1 / m.g12
    return np.linalg.inv(s)


def _mesh(solid, size: float):
    import gmsh
    from build123d import export_brep
    from skfem import MeshTet

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "arm.brep"
        export_brep(solid, path)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.model.occ.importShapes(str(path))
            gmsh.model.occ.synchronize()
            gmsh.option.setNumber("Mesh.CharacteristicLengthMax", size)
            gmsh.option.setNumber("Mesh.CharacteristicLengthMin", size / 3)
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)
            gmsh.model.mesh.generate(3)
            tags, coords, _ = gmsh.model.mesh.getNodes()
            _types, _etags, enodes = gmsh.model.mesh.getElements(3)
        finally:
            gmsh.finalize()
    index = np.zeros(int(tags.max()) + 1, dtype=int)
    index[tags.astype(int)] = np.arange(len(tags))
    p = coords.reshape(-1, 3).T
    t = index[enodes[0].astype(int)].reshape(-1, 4).T
    return MeshTet(np.ascontiguousarray(p), np.ascontiguousarray(t))


def _voigt(e):
    return [e[0, 0], e[1, 1], e[2, 2], 2 * e[1, 2], 2 * e[0, 2], 2 * e[0, 1]]


def analyse(design: str, material: Material = MATERIAL, size: float = MESH_SIZE):
    """Solve the arm of the design the engine is configured for. Returns (Report, plot data)."""
    from scipy.sparse.linalg import eigsh
    from skfem import Basis, BilinearForm, ElementTetP2, ElementVector, FacetBasis, LinearForm, asm, condense, solve
    from skfem.helpers import dot, sym_grad

    sheet = F.SHEETS["arm"]()
    solid = sheet.solid()
    t = sheet.thickness
    edge = P.ARM_BOLT_U[1] + P.LEG_R  # where the plates stop holding the arm
    mesh = _mesh(solid, size)
    basis = Basis(mesh, ElementVector(ElementTetP2()), intorder=4)
    c = _stiffness_matrix(material)

    @BilinearForm
    def stiffness(u, v, _w):
        a, b = _voigt(sym_grad(u)), _voigt(sym_grad(v))
        return sum(c[i, j] * a[j] * b[i] for i in range(6) for j in range(6) if c[i, j] != 0.0)

    @BilinearForm
    def mass(u, v, _w):
        return material.density * 1e-6 * dot(u, v)  # g/mm3 -> t/mm3: N, mm, s

    k, m = asm(stiffness, basis), asm(mass, basis)

    def held(x):  # both faces, under the plate legs
        return ((np.abs(x[2]) < 1e-6) | (np.abs(x[2] - t) < 1e-6)) & (x[0] <= edge) & (np.abs(x[1]) <= P.LEG_R)

    fixed = basis.get_dofs(held).all()
    centre = (P.ARM_LEN, 0.0)
    bolts = np.array(F.motor_bolts(centre))

    def screw_wall(x):
        d = np.min(np.hypot(x[0][None] - bolts[:, 0, None], x[1][None] - bolts[:, 1, None]), axis=0)
        return d < P.D_M3 / 2 + P.MOTOR_SLOT / 2 + 0.25

    wall = FacetBasis(mesh, basis.elem, facets=mesh.facets_satisfying(screw_wall, boundaries_only=True), intorder=4)
    scalar_wall = FacetBasis(mesh, ElementTetP2(), facets=wall.find, intorder=4)
    wall_area = float(asm(LinearForm(lambda v, _w: v), scalar_wall).sum())
    wall_dofs = basis.get_dofs(facets=wall.find)

    # pad dofs carry the motor: its mass is spread over the screw-hole walls
    m_tip = m.copy().tolil()
    for comp in range(3):
        idx = wall_dofs.nodal[f"u^{comp + 1}"] if hasattr(wall_dofs, "nodal") else []
        if len(idx):
            share = TIP_MASS * 1e-6 / len(idx)
            for d in idx:
                m_tip[d, d] += share
    m_tip = m_tip.tocsr()

    evaluate = Basis(mesh, ElementVector(ElementTetP2()), intorder=2)
    centroids = mesh.p[:, mesh.t].mean(axis=1)
    p0, p1, p2, p3 = (mesh.p[:, mesh.t[i]] for i in range(4))
    volumes = np.abs(np.einsum("ij,ij->j", p1 - p0, np.cross(p2 - p0, p3 - p0, axis=0))) / 6
    free = centroids[0] > edge + 0.5
    pad = np.hypot(centroids[0] - centre[0], centroids[1]) < P.MOTOR_PAD_R  # load introduction: not judged

    def percentile(values: np.ndarray, where: np.ndarray, q: float = 0.995) -> float:
        v, w = values[where], volumes[where]
        order = np.argsort(v)
        cum = np.cumsum(w[order]) / w.sum()
        return float(v[order][np.searchsorted(cum, q)])

    cases, fields = {}, {}
    for name, direction in (("vertical", 2), ("side", 1)):

        @LinearForm
        def load(v, _w, direction=direction):
            return v[direction] / wall_area  # 1 N spread over the screw-hole walls

        f = asm(load, wall)
        u = solve(*condense(k, f, D=fixed))
        tip = float(np.mean(u[wall_dofs.nodal[f"u^{direction + 1}"]]))
        grad = evaluate.interpolate(u).grad
        strain = 0.5 * (grad + np.transpose(grad, (1, 0, 2, 3)))
        ev = np.array(_voigt(strain))  # 6 x elements x points
        stress = np.einsum("ij,jkl->ikl", c, ev).mean(axis=2)  # element means
        fibre = np.maximum(np.abs(stress[0]), np.abs(stress[1]))
        shear = np.maximum(np.abs(stress[3]), np.abs(stress[4]))
        judged = free & ~pad
        s_f, s_s = percentile(fibre, judged), percentile(shear, judged)
        load_f, load_s = material.strength / s_f, material.shear / s_s
        usage = np.maximum(fibre / material.strength, shear / material.shear)
        hot = judged & (usage >= np.quantile(usage[judged], 0.99))
        cases[name] = Case(
            1 / tip,
            s_f,
            s_s,
            min(load_f, load_s),
            "fibre stress" if load_f <= load_s else "interlaminar shear",
            float(np.average(centroids[0][hot], weights=volumes[hot])),
        )
        fields[name] = usage * min(load_f, load_s)  # usage at the failure load: 1.0 = at the allowable

    free_dofs = np.setdiff1d(np.arange(k.shape[0]), fixed)
    lam = eigsh(k[free_dofs][:, free_dofs], k=4, M=m_tip[free_dofs][:, free_dofs], sigma=0.0, which="LM")[0]
    freqs = [float(np.sqrt(max(v, 0.0)) / (2 * np.pi)) for v in sorted(lam)]

    report = Report(
        design,
        t,
        P.ARM_LEN - edge,
        float(solid.volume * material.density),
        mesh.p.shape[1],
        mesh.t.shape[1],
        cases["vertical"],
        cases["side"],
        freqs,
    )
    return report, {"mesh": mesh, "fields": fields}


def plot(data: dict, png: Path, case: str = "side", size: tuple[int, int] = (1600, 520)) -> Path:
    """Top view of the arm coloured by how much of the allowable is used at the failure load."""
    import vtk

    mesh, values = data["mesh"], data["fields"][case]
    nodal, count = np.zeros(mesh.p.shape[1]), np.zeros(mesh.p.shape[1])
    for i in range(4):
        np.add.at(nodal, mesh.t[i], values)
        np.add.at(count, mesh.t[i], 1)
    nodal /= np.maximum(count, 1)
    facets = mesh.facets[:, mesh.boundary_facets()]
    points = vtk.vtkPoints()
    for x, y, z in mesh.p.T:
        points.InsertNextPoint(float(x), float(y), float(z))
    cells = vtk.vtkCellArray()
    for a, b, c in facets.T:
        cells.InsertNextCell(3, (int(a), int(b), int(c)))
    scal = vtk.vtkFloatArray()
    scal.SetName("usage")
    for v in nodal:
        scal.InsertNextValue(float(min(v, 1.2)))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    poly.GetPointData().SetScalars(scal)
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.66, 0.0)
    lut.SetNumberOfTableValues(64)
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(0.0, 1.0)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().LightingOff()
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    ren.AddActor(actor)
    bar = vtk.vtkScalarBarActor()
    bar.SetLookupTable(lut)
    bar.SetTitle("share of allowable")
    bar.SetNumberOfLabels(5)
    bar.GetLabelTextProperty().SetColor(0.1, 0.1, 0.1)
    bar.GetTitleTextProperty().SetColor(0.1, 0.1, 0.1)
    bar.SetOrientationToHorizontal()
    bar.SetWidth(0.34)
    bar.SetHeight(0.14)
    bar.SetPosition(0.62, 0.04)
    ren.AddViewProp(bar)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(*size)
    win.AddRenderer(ren)
    cam = ren.GetActiveCamera()
    cam.SetParallelProjection(True)
    cam.SetPosition(P.ARM_LEN / 2, 0, 500)
    cam.SetFocalPoint(P.ARM_LEN / 2, 0, 0)
    cam.SetViewUp(0, 1, 0)
    ren.ResetCamera()
    cam.Zoom(1.9)
    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.Update()
    png.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(png))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    return png
